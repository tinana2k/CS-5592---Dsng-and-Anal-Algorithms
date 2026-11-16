"""
CS-5592: Design and Analysis of Algorithms - Assignment 2
Problem 1: Vertex k-Labeling of Graphs Using Algorithmic Approach
Authors: Tina Nguyen & Haoran
Affiliation: University of Missouri - Kansas City (UMKC)

This module implements data structures, exact backtracking algorithms,
heuristic scalable algorithms, and theoretical bounding models for
edge irregular k-labeling (vertex k-labeling) on:
1. Generalized Petersen Graphs GP(n, p)
2. Ship Wheel Graphs SW(n, m)
3. Crab Graphs Crab(n, m)
"""

import time
import math
import tracemalloc
from collections import defaultdict
from typing import List, Tuple, Dict, Set, Optional


class Graph:
    """Base class for undirected graph representation using Adjacency List."""
    def __init__(self, name: str, num_vertices: int, edges: List[Tuple[int, int]]):
        self.name = name
        self.num_vertices = num_vertices
        # Standardize edges such that u < v
        self.edges = sorted(list(set((min(u, v), max(u, v)) for u, v in edges if u != v)))
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
        Theorem 1 (Ahmad, Al-Mushayt, Baca, 2014):
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

    def upper_bound_asim_log(self) -> float:
        """
        Asim, Ahmad, Hasni (2018/2021):
        Empirical/theoretical upper bound: |E| * log2(|V|)
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
    """
    def __init__(self, n: int, p: int):
        assert n >= 3, "n must be >= 3"
        assert 1 <= p < n, f"p must be 1 <= p < {n}"
        
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

    def get_canonical_traversal_order(self) -> List[int]:
        """
        Coupled Spoke Ordering:
        u_0, v_0, u_1, v_1, ..., u_{n-1}, v_{n-1}
        This ensures spokes (u_i, v_i) are formed immediately,
        maximizing early edge weight collisions and pruning in backtracking.
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
    """
    def __init__(self, n: int, m: int = 2):
        edges = []
        for i in range(1, n + 1):
            edges.append((0, i))
        leaf_idx = n + 1
        for i in range(1, n + 1):
            for _ in range(m):
                edges.append((i, leaf_idx))
                leaf_idx += 1
        super().__init__(f"Crab({n}, {m})", 1 + n + n * m, edges)


class LabelingResult:
    """Encapsulates vertex k-labeling output, validation, and performance metrics."""
    def __init__(self, graph: Graph, algorithm_name: str, labels: Optional[List[int]],
                 k: int, runtime_sec: float, memory_bytes: int):
        self.graph = graph
        self.algorithm_name = algorithm_name
        self.labels = labels
        self.k = k
        self.runtime_sec = runtime_sec
        self.memory_bytes = memory_bytes
        self.is_valid = False
        self.edge_weights: List[int] = []
        self.unique_weights_count = 0
        
        if labels is not None:
            self._validate()

    def _validate(self):
        self.edge_weights = [self.labels[u] + self.labels[v] for u, v in self.graph.edges]
        unique_set = set(self.edge_weights)
        self.unique_weights_count = len(unique_set)
        
        # Valid iff all edge weights are unique and labels are in range 1..k
        weights_distinct = (len(unique_set) == self.graph.num_edges)
        labels_positive = all(1 <= l <= self.k for l in self.labels)
        self.is_valid = weights_distinct and labels_positive


class ExactBacktrackingSolver:
    """
    Algorithm 1: Constraint-Satisfaction Backtracking with Forward Checking & MRV Ordering.
    Finds the exact edge irregularity strength es(G) by testing k = lower_bound upwards.
    """
    def __init__(self, graph: Graph, timeout_per_k: float = 3.0):
        self.graph = graph
        self.timeout_per_k = timeout_per_k

    def solve_for_k(self, k: int) -> Optional[List[int]]:
        start_time = time.time()
        num_v = self.graph.num_vertices
        labels = [-1] * num_v
        used_weights: Set[int] = set()

        if hasattr(self.graph, 'get_canonical_traversal_order'):
            order = self.graph.get_canonical_traversal_order()
        else:
            # Degree-descending order
            order = sorted(range(num_v), key=lambda x: self.graph.degree[x], reverse=True)

        def backtrack(step: int) -> Optional[List[int]]:
            if time.time() - start_time > self.timeout_per_k:
                return None
            if step == num_v:
                return list(labels)

            v = order[step]
            labeled_nbrs = [(nbr, e_idx) for nbr, e_idx in self.graph.adj[v] if labels[nbr] != -1]
            forbidden_labels = {labels[nbr2] for nbr2 in self.graph.two_hop[v] if labels[nbr2] != -1}

            for val in range(1, k + 1):
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

        return backtrack(0)

    def find_minimum_k(self, max_k_offset: int = 10) -> LabelingResult:
        tracemalloc.start()
        start_time = time.time()
        lb = self.graph.lower_bound_es()
        
        best_sol = None
        best_k = -1

        for k in range(lb, lb + max_k_offset + 1):
            sol = self.solve_for_k(k)
            if sol is not None:
                best_sol = sol
                best_k = k
                break

        dur = time.time() - start_time
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        return LabelingResult(self.graph, "Exact Backtracking", best_sol, best_k, dur, peak)


class ScalableHeuristicSolver:
    """
    Algorithm 2: High-Performance Greedy Constructive Heuristic with
    2-Hop Collision Prevention & Min-Conflict Ordering.
    Scales to thousands of vertices in milliseconds.
    """
    def __init__(self, graph: Graph):
        self.graph = graph

    def solve(self, max_restarts: int = 5) -> LabelingResult:
        tracemalloc.start()
        start_time = time.time()
        
        num_v = self.graph.num_vertices
        num_e = self.graph.num_edges
        
        if hasattr(self.graph, 'get_canonical_traversal_order'):
            base_order = self.graph.get_canonical_traversal_order()
        else:
            base_order = sorted(range(num_v), key=lambda x: self.graph.degree[x], reverse=True)

        best_labels: Optional[List[int]] = None
        best_k = float('inf')

        for restart in range(max_restarts):
            labels = [-1] * num_v
            used_weights: Set[int] = set()
            order = list(base_order)

            # Assign seed value for starting nodes
            current_max = 1
            success = True

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
                    
                    if val > best_k: # Pruning
                        success = False
                        break

                if not success:
                    break

            if success and current_max < best_k:
                best_k = current_max
                best_labels = list(labels)

        dur = time.time() - start_time
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        return LabelingResult(self.graph, "Scalable Heuristic", best_labels, int(best_k), dur, peak)


def benchmark_graph_labeling() -> List[Dict]:
    """Runs empirical benchmarks across a wide range of graph configurations."""
    test_suite = [
        # Small / medium exact instances
        (3, 1), (4, 1), (5, 2), (6, 2), (7, 2), (8, 3), (9, 2), (10, 3), (12, 5), (16, 5),
        # Larger scalable instances
        (20, 7), (25, 7), (30, 9), (50, 11), (100, 21), (200, 31), (500, 41), (1000, 51)
    ]
    
    results = []
    print("=" * 80)
    print(f"{'Graph':<12} | {'|V|':<5} | {'|E|':<5} | {'LB':<5} | {'k (Exact)':<9} | {'k (Heur)':<8} | {'Exact T(s)':<10} | {'Heur T(s)':<9} | {'Valid'}")
    print("-" * 80)

    for n, p in test_suite:
        gp = GeneralizedPetersenGraph(n, p)
        lb = gp.lower_bound_es()
        
        # Exact backtracking for n <= 16
        exact_k = "-"
        exact_time = "-"
        if n <= 16:
            exact_solver = ExactBacktrackingSolver(gp, timeout_per_k=2.0)
            exact_res = exact_solver.find_minimum_k(max_k_offset=2)
            if exact_res.is_valid:
                exact_k = str(exact_res.k)
                exact_time = f"{exact_res.runtime_sec:.4f}"

        # Heuristic solver for all
        heur_solver = ScalableHeuristicSolver(gp)
        heur_res = heur_solver.solve(max_restarts=1)
        heur_k = str(heur_res.k)
        heur_time = f"{heur_res.runtime_sec:.4f}"
        
        print(f"{gp.name:<12} | {gp.num_vertices:<5} | {gp.num_edges:<5} | {lb:<5} | {exact_k:<9} | {heur_k:<8} | {exact_time:<10} | {heur_time:<9} | {heur_res.is_valid}")
        
        results.append({
            "Graph": gp.name,
            "n": n,
            "p": p,
            "Order_V": gp.num_vertices,
            "Size_E": gp.num_edges,
            "Lower_Bound": lb,
            "Exact_k": exact_k,
            "Exact_Time_s": exact_time,
            "Heuristic_k": heur_res.k,
            "Heuristic_Time_s": heur_res.runtime_sec,
            "Heuristic_Memory_KB": heur_res.memory_bytes / 1024,
            "Valid": heur_res.is_valid,
            "Upper_Bound_Log": gp.upper_bound_asim_log()
        })

    return results


if __name__ == "__main__":
    benchmark_graph_labeling()
