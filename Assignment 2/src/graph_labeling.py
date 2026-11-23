"""
CS-5592: Design and Analysis of Algorithms - Assignment 2
Problem 1: Vertex k-Labeling of Graphs Using Algorithmic Approach
Authors: Tina Nguyen (qpnh58@umsystem.edu) & Haoran (hzwkg@umsystem.edu)
Affiliation: University of Missouri - Kansas City (UMKC)

This module implements data structures, exact constraint backtracking,
greedy constructive algorithms, and theoretical bounding models for
edge irregular k-labeling (vertex k-labeling) on:
1. Generalized Petersen Graphs GP(n, p)
2. Ship Wheel Graphs SW(n, m)
3. Crab Graphs Crab(n, m)
"""

import time
import math
import tracemalloc
from collections import defaultdict
from typing import List, Tuple, Dict, Set, Optional, Any


class SearchStatus:
    FOUND = "FOUND"
    PROVEN_UNSAT = "PROVEN_UNSAT"
    TIMEOUT = "TIMEOUT"


class Graph:
    """Base class for undirected simple graph representation using Adjacency List."""
    def __init__(self, name: str, num_vertices: int, edges: List[Tuple[int, int]]):
        if num_vertices <= 0:
            raise ValueError(f"num_vertices must be positive, got {num_vertices}")
        self.name = name
        self.num_vertices = num_vertices

        # Defensive input validation: reject out-of-bounds, self-loops, and duplicate edges
        validated_edges = []
        seen = set()
        for idx, (u, v) in enumerate(edges):
            if not (0 <= u < num_vertices and 0 <= v < num_vertices):
                raise ValueError(f"Edge {idx} ({u}, {v}) has vertex index out of bounds [0, {num_vertices-1}]")
            if u == v:
                raise ValueError(f"Self-loop detected at vertex {u}. Simple graphs only.")
            edge_norm = (min(u, v), max(u, v))
            if edge_norm in seen:
                raise ValueError(f"Duplicate edge detected: ({u}, {v}). Simple graphs only.")
            seen.add(edge_norm)
            validated_edges.append(edge_norm)

        self.edges = sorted(validated_edges)
        self.num_edges = len(self.edges)

        # Build adjacency list: node -> list of (neighbor, edge_index)
        self.adj = [[] for _ in range(num_vertices)]
        self.degree = [0] * num_vertices
        for e_idx, (u, v) in enumerate(self.edges):
            self.adj[u].append((v, e_idx))
            self.adj[v].append((u, e_idx))
            self.degree[u] += 1
            self.degree[v] += 1

        self.max_degree = max(self.degree) if self.degree else 0
        self.min_degree = min(self.degree) if self.degree else 0

        # Precompute 2-hop neighborhood (vertices sharing a common neighbor)
        # In vertex k-labeling, two neighbors of any vertex CANNOT have the same label,
        # otherwise their incident edges from that vertex would have identical weights.
        self.two_hop = [set() for _ in range(num_vertices)]
        for v in range(num_vertices):
            for nbr, _ in self.adj[v]:
                for nbr2, _ in self.adj[nbr]:
                    if nbr2 != v:
                        self.two_hop[v].add(nbr2)

    def lower_bound_es(self) -> int:
        """
        Theorem 1 (Ahmad, Al-Mushayt, Bača, 2014):
        es(G) >= max( ceil((|E(G)| + 1) / 2), Delta(G) )
        """
        formula_bound = math.ceil((self.num_edges + 1) / 2)
        return max(formula_bound, self.max_degree)

    def upper_bound_fibonacci(self) -> int:
        """
        Theorem 2 (Ahmad et al., 2014):
        es(G) <= F_{|V|} where F_1=1, F_2=2, F_n = F_{n-1} + F_{n-2}.
        """
        if self.num_vertices <= 1:
            return 1
        a, b = 1, 2
        for _ in range(3, self.num_vertices + 1):
            a, b = b, a + b
        return b

    def reference_bound_asim_log(self) -> float:
        """
        Literature reference curve from Asim, Ahmad, Hasni (2018/2021):
        |E| * log2(|V|). Originally established for circulant graphs.
        Provided here as an empirical reference curve, not a proven theorem for all GP graphs.
        """
        if self.num_vertices <= 1:
            return float(self.num_edges)
        return self.num_edges * math.log2(self.num_vertices)


class GeneralizedPetersenGraph(Graph):
    """
    Generalized Petersen Graph GP(n, p).
    Order: 2n (outer cycle u_0..u_{n-1}, inner star v_0..v_{n-1})
    Size: 3n (n outer edges, n spokes, n inner edges)
    Regularity: 3-regular cubic graph (Delta = 3).

    Domain requirement for a simple, 3-regular GP(n, p):
    n >= 3 and 1 <= p < n / 2.
    (When p = n/2 for even n, inner chords connect identical vertex pairs, violating 3-regularity).
    """
    def __init__(self, n: int, p: int):
        if n < 3:
            raise ValueError(f"n must be >= 3, got n={n}")
        if not (1 <= p < n / 2):
            raise ValueError(f"For a simple 3-regular GP(n, p), parameter p must satisfy 1 <= p < n/2 (got n={n}, p={p})")

        edges = []
        # Outer cycle: (u_i, u_{i+1})
        for i in range(n):
            edges.append((i, (i + 1) % n))
        # Spokes: (u_i, v_i)
        for i in range(n):
            edges.append((i, n + i))
        # Inner star: (v_i, v_{i+p})
        for i in range(n):
            edges.append((n + i, n + ((i + p) % n)))

        super().__init__(f"GP({n}, {p})", 2 * n, edges)
        self.n = n
        self.p = p

        # Assert strict topological invariants
        assert self.num_vertices == 2 * n, f"Expected 2n={2*n} vertices, got {self.num_vertices}"
        assert self.num_edges == 3 * n, f"Expected 3n={3*n} edges, got {self.num_edges}"
        assert all(d == 3 for d in self.degree), f"All vertices must have degree 3, got degrees {self.degree}"

    def get_canonical_traversal_order(self) -> List[int]:
        """
        Coupled Spoke Ordering:
        u_0, v_0, u_1, v_1, ..., u_{n-1}, v_{n-1}
        Interleaves outer and inner spoke endpoints so spoke (u_i, v_i)
        is formed immediately at step 2i+1.
        """
        order = []
        for i in range(self.n):
            order.append(i)          # u_i
            order.append(self.n + i)   # v_i
        return order


class ShipWheelGraph(Graph):
    """
    Ship Wheel Graph SW(n, m).
    Hub vertex: 0
    Rim vertices: 1..n forming a cycle C_n
    Pendant rim leaves: m leaves attached to each rim vertex.
    Order: 1 + n + n * m
    Size: n (hub spokes) + n (rim cycle) + n * m (leaves)
    """
    def __init__(self, n: int, m: int = 2):
        if n < 3:
            raise ValueError(f"Rim size n must be >= 3, got n={n}")
        if m < 1:
            raise ValueError(f"Leaves per rim vertex m must be >= 1, got m={m}")

        edges = []
        # Hub to rim
        for i in range(1, n + 1):
            edges.append((0, i))
        # Rim cycle
        for i in range(1, n + 1):
            nxt = 1 if i == n else i + 1
            edges.append((i, nxt))
        # Leaves
        leaf_idx = n + 1
        for i in range(1, n + 1):
            for _ in range(m):
                edges.append((i, leaf_idx))
                leaf_idx += 1

        total_v = 1 + n + n * m
        super().__init__(f"ShipWheel({n}, {m})", total_v, edges)
        self.rim_size = n
        self.leaves_per_rim = m


class CrabGraph(Graph):
    """
    Crab Graph Crab(n, m).
    Head/center: 0
    Body nodes: 1..n attached to head.
    Legs: m leaves attached to each body node.
    Order: 1 + n + n * m
    Size: n (head to body) + n * m (legs)
    """
    def __init__(self, n: int, m: int = 2):
        if n < 1:
            raise ValueError(f"Body count n must be >= 1, got n={n}")
        if m < 1:
            raise ValueError(f"Legs per body m must be >= 1, got m={m}")

        edges = []
        for i in range(1, n + 1):
            edges.append((0, i))
        leaf_idx = n + 1
        for i in range(1, n + 1):
            for _ in range(m):
                edges.append((i, leaf_idx))
                leaf_idx += 1
        super().__init__(f"Crab({n}, {m})", 1 + n + n * m, edges)
        self.body_count = n
        self.legs_per_body = m


class LabelingResult:
    """Encapsulates vertex k-labeling output, validation, and performance metrics."""
    def __init__(self, graph: Graph, algorithm_name: str, labels: Optional[List[int]],
                 k: int, runtime_sec: float, memory_bytes: int,
                 search_status: str = SearchStatus.FOUND,
                 is_exact_minimal: bool = False,
                 nodes_explored: int = 0):
        self.graph = graph
        self.algorithm_name = algorithm_name
        self.labels = labels
        self.k = k
        self.runtime_sec = runtime_sec
        self.memory_bytes = memory_bytes
        self.search_status = search_status
        self.is_exact_minimal = is_exact_minimal
        self.nodes_explored = nodes_explored
        self.is_valid = False
        self.edge_weights: List[int] = []
        self.unique_weights_count = 0

        if labels is not None:
            if len(labels) != graph.num_vertices:
                raise ValueError(f"Label count {len(labels)} does not match graph vertices {graph.num_vertices}")
            self._validate()

    def _validate(self):
        self.edge_weights = [self.labels[u] + self.labels[v] for u, v in self.graph.edges]
        unique_set = set(self.edge_weights)
        self.unique_weights_count = len(unique_set)

        weights_distinct = (len(unique_set) == self.graph.num_edges)
        labels_positive = all(1 <= l <= self.k for l in self.labels)
        self.is_valid = weights_distinct and labels_positive


class ExactBacktrackingSolver:
    """
    Algorithm 1: Depth-First Constraint Backtracking with Early Collision Pruning.
    Uses structural vertex ordering and 2-hop neighborhood conflict pruning.
    Returns explicit status: FOUND, PROVEN_UNSAT, or TIMEOUT.
    """
    def __init__(self, graph: Graph, timeout_per_k: float = 3.0):
        self.graph = graph
        self.timeout_per_k = timeout_per_k

    def solve_for_k(self, k: int, custom_order: Optional[List[int]] = None) -> Tuple[str, Optional[List[int]], int]:
        """
        Solves for a specific k.
        Returns: (status, labels, nodes_explored)
        status: SearchStatus.FOUND, SearchStatus.PROVEN_UNSAT, or SearchStatus.TIMEOUT
        """
        start_time = time.time()
        num_v = self.graph.num_vertices
        labels = [-1] * num_v
        used_weights: Set[int] = set()
        nodes_count = 0
        timed_out = False

        if custom_order is not None:
            order = custom_order
        elif hasattr(self.graph, 'get_canonical_traversal_order'):
            order = self.graph.get_canonical_traversal_order()
        else:
            order = sorted(range(num_v), key=lambda x: self.graph.degree[x], reverse=True)

        def backtrack(step: int) -> Optional[List[int]]:
            nonlocal nodes_count, timed_out
            if time.time() - start_time > self.timeout_per_k:
                timed_out = True
                return None
            if step == num_v:
                return list(labels)

            v = order[step]
            labeled_nbrs = [(nbr, e_idx) for nbr, e_idx in self.graph.adj[v] if labels[nbr] != -1]
            forbidden_labels = {labels[nbr2] for nbr2 in self.graph.two_hop[v] if labels[nbr2] != -1}

            for val in range(1, k + 1):
                if timed_out:
                    return None
                if val in forbidden_labels:
                    continue

                conflict = False
                new_weights = []
                for nbr, e_idx in labeled_nbrs:
                    w = val + labels[nbr]
                    if w in used_weights or w in new_weights:
                        conflict = True
                        break
                    new_weights.append(w)

                if not conflict:
                    nodes_count += 1
                    labels[v] = val
                    for w in new_weights:
                        used_weights.add(w)

                    res = backtrack(step + 1)
                    if res is not None:
                        return res

                    labels[v] = -1
                    for w in new_weights:
                        used_weights.remove(w)

            return None

        sol = backtrack(0)
        if sol is not None:
            return SearchStatus.FOUND, sol, nodes_count
        elif timed_out:
            return SearchStatus.TIMEOUT, None, nodes_count
        else:
            return SearchStatus.PROVEN_UNSAT, None, nodes_count

    def find_minimum_k(self, max_k_offset: int = 10) -> LabelingResult:
        """
        Tests candidate k starting from lower_bound_es() upwards.
        Only marks is_exact_minimal = True if:
        1. Solution found at k == lower_bound (provably minimal since es(G) >= LB), OR
        2. All intermediate k' in [LB, k - 1] were exhaustively PROVEN_UNSAT.
        If any smaller k timed out, the result is marked as a feasible upper bound.
        """
        tracemalloc.start()
        start_time = time.time()
        lb = self.graph.lower_bound_es()

        best_sol = None
        best_k = -1
        proven_unsat_below = True
        overall_status = SearchStatus.TIMEOUT
        total_nodes = 0

        for k in range(lb, lb + max_k_offset + 1):
            status, sol, nodes = self.solve_for_k(k)
            total_nodes += nodes
            if status == SearchStatus.FOUND:
                best_sol = sol
                best_k = k
                overall_status = SearchStatus.FOUND
                break
            elif status == SearchStatus.TIMEOUT:
                proven_unsat_below = False
            elif status == SearchStatus.PROVEN_UNSAT:
                pass

        dur = time.time() - start_time
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        is_minimal = (best_sol is not None) and (best_k == lb or proven_unsat_below)

        return LabelingResult(
            self.graph,
            "Exact Backtracking",
            best_sol,
            best_k,
            dur,
            peak,
            search_status=overall_status,
            is_exact_minimal=is_minimal,
            nodes_explored=total_nodes
        )


class ScalableHeuristicSolver:
    """
    Algorithm 2: Greedy Constructive Labeling with 2-Hop Conflict Avoidance.
    Visits vertices in canonical structural order and greedily assigns the minimum
    positive label satisfying two local invariants:
    (1) val != label of any 2-hop neighbor (prevents incident edge collision)
    (2) val + label(nbr) != any previously assigned edge weight.

    Time Complexity: O(|V| * K * Delta + |V| * Delta^2)
    where Delta is constant (Delta = 3 for GP(n, p)) and K is candidate label search range.
    In practice, hash-set lookups provide near-linear empirical scaling.
    """
    def __init__(self, graph: Graph):
        self.graph = graph

    def solve(self, seed: Optional[int] = None) -> LabelingResult:
        tracemalloc.start()
        start_time = time.time()

        num_v = self.graph.num_vertices

        if hasattr(self.graph, 'get_canonical_traversal_order'):
            order = list(self.graph.get_canonical_traversal_order())
        else:
            order = sorted(range(num_v), key=lambda x: self.graph.degree[x], reverse=True)

        if seed is not None:
            # Deterministic permutation for reproducibility when multiple runs requested
            import random
            rng = random.Random(seed)
            rng.shuffle(order)

        labels = [-1] * num_v
        used_weights: Set[int] = set()
        current_max = 1

        for v in order:
            labeled_nbrs = [nbr for nbr, _ in self.graph.adj[v] if labels[nbr] != -1]
            forbidden_labels = {labels[nbr2] for nbr2 in self.graph.two_hop[v] if labels[nbr2] != -1}

            val = 1
            while True:
                if val in forbidden_labels:
                    val += 1
                    continue

                conflict = False
                new_w = []
                for nbr in labeled_nbrs:
                    w = val + labels[nbr]
                    if w in used_weights or w in new_w:
                        conflict = True
                        break
                    new_w.append(w)

                if not conflict:
                    labels[v] = val
                    for w in new_w:
                        used_weights.add(w)
                    if val > current_max:
                        current_max = val
                    break
                val += 1

        dur = time.time() - start_time
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        return LabelingResult(
            self.graph,
            "Greedy Constructive",
            labels,
            current_max,
            dur,
            peak,
            search_status=SearchStatus.FOUND,
            is_exact_minimal=False
        )


def export_labeling_details(res: LabelingResult) -> Dict[str, Any]:
    """
    Exports full vertex label assignments and induced edge weights.
    Provides complete reproducible per-instance output for arbitrary requested graphs (Task 5).
    """
    if res.labels is None:
        return {"error": "No valid labeling exists for this result"}

    return {
        "graph_name": res.graph.name,
        "order_V": res.graph.num_vertices,
        "size_E": res.graph.num_edges,
        "lower_bound": res.graph.lower_bound_es(),
        "achieved_k": res.k,
        "is_valid": res.is_valid,
        "is_exact_minimal": res.is_exact_minimal,
        "runtime_s": res.runtime_sec,
        "peak_mem_kb": res.memory_bytes / 1024,
        "vertex_labels": {v: res.labels[v] for v in range(res.graph.num_vertices)},
        "edge_weights": [
            {
                "edge": (u, v),
                "phi_u": res.labels[u],
                "phi_v": res.labels[v],
                "weight": res.labels[u] + res.labels[v]
            }
            for u, v in res.graph.edges
        ],
        "distinct_weights_sequence": sorted(res.edge_weights),
        "unique_weights_count": res.unique_weights_count
    }


def compare_traversal_orders(gp: GeneralizedPetersenGraph, k: int, timeout_sec: float = 5.0) -> Dict[str, Any]:
    """
    Measures explored nodes, time, and success between Coupled Spoke Traversal
    and Naive Sequential Cycle Traversal on GP(n, p).
    """
    coupled_order = gp.get_canonical_traversal_order()
    seq_order = list(range(2 * gp.n))

    solver = ExactBacktrackingSolver(gp, timeout_per_k=timeout_sec)
    c_status, c_sol, c_nodes = solver.solve_for_k(k, custom_order=coupled_order)
    s_status, s_sol, s_nodes = solver.solve_for_k(k, custom_order=seq_order)

    return {
        "graph": gp.name,
        "k": k,
        "coupled_spoke": {"status": c_status, "nodes_explored": c_nodes},
        "sequential": {"status": s_status, "nodes_explored": s_nodes}
    }


def benchmark_graph_labeling() -> List[Dict]:
    """
    Runs empirical benchmarks across verified Generalized Petersen Graph instances.
    Enforces valid parameter space 1 <= p < n/2 for all admitted cubic GP graphs.
    """
    test_suite = [
        # Small / medium instances for exact solver evaluation
        (3, 1), (4, 1), (5, 2), (6, 2), (7, 2), (8, 3), (9, 2), (10, 3), (12, 5), (16, 5),
        # Larger scalable instances for greedy heuristic evaluation
        (20, 7), (25, 7), (30, 9), (50, 11), (100, 21), (200, 31), (500, 41), (1000, 51)
    ]

    results = []
    print("=" * 95)
    print(f"{'Graph':<12} | {'|V|':<5} | {'|E|':<5} | {'LB':<5} | {'Exact es':<9} | {'Exact Status':<12} | {'Heur k':<8} | {'Exact T(s)':<10} | {'Heur T(s)':<9} | {'Valid'}")
    print("-" * 95)

    for n, p in test_suite:
        gp = GeneralizedPetersenGraph(n, p)
        lb = gp.lower_bound_es()

        # Exact backtracking for n <= 16
        exact_k = "-"
        exact_status = "-"
        exact_time = "-"
        if n <= 16:
            exact_solver = ExactBacktrackingSolver(gp, timeout_per_k=2.0)
            exact_res = exact_solver.find_minimum_k(max_k_offset=2)
            if exact_res.is_valid and exact_res.is_exact_minimal:
                exact_k = str(exact_res.k)
                exact_status = "OPTIMAL"
                exact_time = f"{exact_res.runtime_sec:.4f}"
            elif exact_res.is_valid:
                exact_k = f"{exact_res.k} (ub)"
                exact_status = "FEASIBLE"
                exact_time = f"{exact_res.runtime_sec:.4f}"
            else:
                exact_status = "TIMEOUT"

        # Greedy heuristic solver for all
        heur_solver = ScalableHeuristicSolver(gp)
        heur_res = heur_solver.solve()
        heur_k = str(heur_res.k)
        heur_time = f"{heur_res.runtime_sec:.4f}"

        print(f"{gp.name:<12} | {gp.num_vertices:<5} | {gp.num_edges:<5} | {lb:<5} | {exact_k:<9} | {exact_status:<12} | {heur_k:<8} | {exact_time:<10} | {heur_time:<9} | {heur_res.is_valid}")

        results.append({
            "Graph": gp.name,
            "n": n,
            "p": p,
            "Order_V": gp.num_vertices,
            "Size_E": gp.num_edges,
            "Lower_Bound": lb,
            "Exact_k": exact_k,
            "Exact_Status": exact_status,
            "Exact_Time_s": exact_time,
            "Heuristic_k": heur_res.k,
            "Heuristic_Time_s": heur_res.runtime_sec,
            "Heuristic_Memory_KB": heur_res.memory_bytes / 1024,
            "Valid": heur_res.is_valid,
            "Upper_Bound_Log": gp.reference_bound_asim_log()
        })

    return results


if __name__ == "__main__":
    benchmark_graph_labeling()
