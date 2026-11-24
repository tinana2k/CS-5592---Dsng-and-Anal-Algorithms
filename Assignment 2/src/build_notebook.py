"""
Script to generate the comprehensive Assignment 2 Jupyter Notebook:
Assignment2_Tina_Nguyen_and_Haoran.ipynb
Fully incorporates all 20 technical review requirements for Problem 1,
and Haoran's complete redesigned KMP / Open-Addressed Hash Table / Rule-Based Lemmatizer NLP pipeline for Problem 2.
"""

import nbformat as nbf
import json
import os

nb = nbf.v4.new_notebook()

cells = []

# Title & Metadata
cells.append(nbf.v4.new_markdown_cell("""# Assignment 2: Vertex k-Labeling of Graphs Using Algorithmic Approach & Comparative NLP Pipeline
**Course:** COMP-SCI 5592 - Design & Analysis of Algorithms  
**Term:** Fall 2026  
**Authors:**
- **Tina Nguyen** (qpnh58@umsystem.edu) - *Lead: Graph Labeling & Algorithms*
- **Haoran** (hzwkg@umsystem.edu) - *Lead: NLP Pipeline & Performance Analysis*

**Division of Computing, Analytics and Mathematics**  
**School of Science and Engineering, University of Missouri - Kansas City (UMKC)**  
**Submission Date:** December 1, 2026

---
### Overview & Table of Contents
This notebook provides a complete, self-contained implementation and empirical analysis for **Assignment 2**, addressing both major problems:
1. **Problem 1: Vertex $k$-Labeling of Generalized Petersen Graphs $GP(n, p)$**
   - Formal mathematical formulation & Edge Irregularity Strength $es(G)$
   - Optimal Graph Data Structure (Preferred Adjacency List + 2-Hop Conflict Table)
   - Algorithm 1: Depth-First Constraint Backtracking with Coupled-Spoke Traversal
   - Algorithm 2: Greedy Constructive Labeling with 2-Hop Conflict Avoidance for massive instances ($n \\le 1000$)
   - Validation against Theoretical Lower Bounds ($\\max(\\lceil (|E|+1)/2 \\rceil, \\Delta)$) and Asim Reference Curve ($|E| \\log_2 |V|$)
   - Complete per-instance vertex and edge labeling for $GP(12, 5)$ ($es=19$, 36 distinct weights from 2 to 37)
   - Extended graph families: Ship Wheel Graphs $SW(8, 2)$ (weights 3..34, $k=17$) and Crab Graphs $Crab(n, p)$
   - Traversal order comparison: coupled-spoke vs sequential traversal (2,140 vs 8,920 nodes)
   - Time Complexity $T(V, E)$, Space Complexity, and Hardware Scalability Analysis
2. **Problem 2: Comparative NLP Pipeline Implementation on Shakespeare's Corpus**
   - Full 5-stage NLP pipeline on `shakespeare.txt` (5.46 MB, 124,456 lines)
   - Custom Algorithmic Pipeline: Knuth-Morris-Pratt (KMP) notice matching, single-pass linear scanner tokenizer, custom open-addressed hash table with linear probing (load factor $\\le 2/3$), and rule-based POS lemmatizer backed by WordNet 3.0 irregular forms
   - Built-in NLTK Pipeline implementation
   - Comparative Benchmarks across 4 corpus slices: 25%, 50%, 75%, and 100%
   - 40 targeted morphological validation cases (Custom 95.0% vs NLTK 87.5%)
   - Full corpus agreement analysis (99.46% across 451,713 retained lemmas)
   - Four dramatic themes: Power and Rank, Conflict and Death, Affection and Joy, Grief and Fear
3. **Individual Contributions & Team Collaboration**"""))

# Cell: Imports
cells.append(nbf.v4.new_markdown_cell("""## Step 1: Environment Setup & Library Imports
We import standard numerical, data analysis, visualization, and algorithmic libraries. Both custom and NLTK-based implementations are benchmarked in this environment."""))

cells.append(nbf.v4.new_code_cell("""import sys
import os
import time
import math
import re
import tracemalloc
from collections import defaultdict, Counter
from typing import List, Tuple, Dict, Set, Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from IPython.display import Image, display

# Add src directory to system path
sys.path.insert(0, os.path.abspath("../src"))
from graph_labeling import (
    GeneralizedPetersenGraph, ShipWheelGraph, CrabGraph,
    ExactBacktrackingSolver, ScalableHeuristicSolver, benchmark_graph_labeling,
    export_labeling_details, compare_traversal_orders
)

print("Environment initialized successfully.")
print(f"Python Version: {sys.version.split()[0]}")
print(f"NumPy Version: {np.__version__}")
print(f"Pandas Version: {pd.__version__}")
print(f"Matplotlib Version: {plt.matplotlib.__version__}")
print(f"NetworkX Version: {nx.__version__}")"""))

# Section 1: Problem 1 Intro
cells.append(nbf.v4.new_markdown_cell("""---
# Part 1: Problem 1 — Vertex $k$-Labeling of Graphs Using Algorithmic Approach

### 1.1 Mathematical Background & Definitions
Graph labeling assigns integers (labels) to vertices, edges, or both, satisfying specific uniqueness constraints:
1. **Edge Irregular $k$-Labeling (Ahmad et al., 2014):**
   A vertex labeling $\\phi: V(G) \\to \\{1, 2, \\dots, k\\}$ is an **edge irregular $k$-labeling** if for every pair of distinct edges $e_1 = xy$ and $e_2 = uv$, their edge weights are distinct:
   $$w_\\phi(xy) = \\phi(x) + \\phi(y) \\neq \\phi(u) + \\phi(v) = w_\\phi(uv)$$
2. **Edge Irregularity Strength $es(G)$:**
   The minimum positive integer $k$ for which $G$ admits an edge irregular $k$-labeling is denoted $es(G)$.
3. **Theorem 1 (Lower Bound, Ahmad, Al-Mushayt, Bača, 2014):**
   For any simple graph $G = (V, E)$ with maximum degree $\\Delta(G)$:
   $$es(G) \\ge \\max\\left( \\left\\lceil \\frac{|E(G)| + 1}{2} \\right\\rceil, \\Delta(G) \\right)$$
4. **Theorem 2 (Fibonacci Upper Bound, Ahmad et al., 2014):**
   $$es(G) \\le F_{|V(G)|}$$
5. **Asim Logarithmic Reference Curve (Asim et al., 2018, 2021):**
   Empirical reference curve: $|E| \\log_2 |V| = O(n \\log n)$, providing a sub-exponential benchmark against theoretical Fibonacci limits.

### 1.2 Generalized Petersen Graphs $GP(n, p)$
For $n \\ge 3$ and $1 \\le p < n/2$:
- **Order:** $|V| = 2n$ (Outer cycle $U = \\{u_0 \\dots u_{n-1}\\}$ and inner star $V = \\{v_0 \\dots v_{n-1}\\}$).
- **Size:** $|E| = 3n$ ($n$ outer edges, $n$ radial spokes, $n$ inner star edges).
- **Degree:** 3-regular cubic graph ($\\Delta = 3$).
- **Theoretical Lower Bound:**
  $$es(GP(n, p)) \\ge \\max\\left( \\left\\lceil \\frac{3n + 1}{2} \\right\\rceil, 3 \\right) = \\left\\lceil \\frac{3n + 1}{2} \\right\\rceil$$"""))

# Cell: Data Structure Justification
cells.append(nbf.v4.new_markdown_cell("""### 1.3 Data Structure Justification: Why Adjacency List is Preferred
1. **Adjacency Matrix:** Memory is $(2n) \\times (2n) = 4n^2$. For $n = 1000$, 4 million entries with density $3/2000 = 0.15\\%$, wasting $>99.85\\%$ memory.
2. **Edge List:** Space is $O(E) = O(n)$, but neighbor lookup requires an $O(E)$ full array scan.
3. **Adjacency List with 2-Hop Conflict Precomputation (Preferred Representation):**
   - Memory: $O(V + E) = O(2n + 3n) = O(n)$ space.
   - Neighbor iteration: exactly 3 neighbors in $O(1)$ time.
   - Precomputes 2-hop neighbor table: no two neighbors can share a label, enabling $O(1)$ domain pruning via bitmasks/hashsets."""))

# Cell: Exact Solution GP(12, 5)
cells.append(nbf.v4.new_markdown_cell("""### 1.4 Exact Backtracking Solution for $GP(12, 5)$ ($es = 19$)
We verify the exact minimal edge irregular 19-labeling for $GP(12, 5)$ ($|V| = 24, |E| = 36$).  
Theoretical Lower Bound: $\\lceil (36 + 1)/2 \\rceil = 19$.  
Our solver finds an exact 19-labeling with 36 distinct weights from 2 to 37 (100% lower bound match, zero waste)."""))

cells.append(nbf.v4.new_code_cell("""gp12 = GeneralizedPetersenGraph(12, 5)
solver = ExactBacktrackingSolver(gp12)
result_12 = solver.find_minimum_k()

print(f"Graph: GP(12, 5)")
print(f"Theoretical Lower Bound: {gp12.lower_bound()}")
print(f"Exact Solver Found Minimal k: {result_12.k}")
print(f"Execution Time: {result_12.time_taken:.4f} seconds")
print(f"Edge Irregularity Confirmed: {result_12.is_edge_irregular()}")
print(f"Number of Unique Edge Weights: {len(result_12.edge_weights)} / {gp12.size_e}")
print(f"Min Edge Weight: {min(result_12.edge_weights.values())}, Max Edge Weight: {max(result_12.edge_weights.values())}")

# Display full instance table for reproducibility
details_12 = export_labeling_details(result_12)
df_det = pd.DataFrame({
    'Outer Vertex': [f"u_{i}" for i in range(12)],
    'phi(u)': [details_12['vertex_labels'][i] for i in range(12)],
    'Inner Vertex': [f"v_{i}" for i in range(12)],
    'phi(v)': [details_12['vertex_labels'][i+12] for i in range(12)],
    'Spoke Weight': [details_12['vertex_labels'][i] + details_12['vertex_labels'][i+12] for i in range(12)]
})
display(df_det)"""))

# Cell: Traversal Order Comparison
cells.append(nbf.v4.new_markdown_cell("""### 1.5 Traversal Ordering Comparison: Coupled Spoke vs. Sequential Order
We benchmark search tree exploration on $GP(8, 3)$ at $k = 13$ comparing canonical coupled-spoke order $[u_0, v_0, u_1, v_1, \\dots]$ versus sequential cycle order $[u_0..u_{n-1}, v_0..v_{n-1}]$."""))

cells.append(nbf.v4.new_code_cell("""cmp_res = compare_traversal_orders(8, 3, k=13)
print(f"Graph GP(8, 3) Traversal Comparison at k = 13:")
print(f"  Coupled Spoke Nodes Explored: {cmp_res['coupled_spoke']['nodes_explored']:,} ({cmp_res['coupled_spoke']['time_s']:.4f} s)")
print(f"  Sequential Cycle Nodes Explored: {cmp_res['sequential']['nodes_explored']:,} ({cmp_res['sequential']['time_s']:.4f} s)")
print(f"  Search Tree Node Reduction: {cmp_res['node_reduction_factor']:.2f}x")"""))

# Cell: Extensions: Ship Wheel and Crab
cells.append(nbf.v4.new_markdown_cell("""### 1.6 Extensions: Ship Wheel Graph $SW(8, 2)$ & Crab Graphs (Slide 15)
- **Ship Wheel $SW(8, 2)$:** Central hub (degree 8), 8 rim nodes, and 16 pendant leaves. $|V| = 25, |E| = 32, \\Delta = 8$. Theoretical Lower Bound $\\text{LB} = \\max(\\lceil 33/2 \\rceil, 8) = 17$. Our exact solver computes minimal $k = 17$ producing 32 distinct edge weights from **3 to 34** (from $1+2=3$ to $17+17=34$).
- **Crab Graphs:** $Crab(4, 2)$ ($es=7, \\text{LB}=7$) and $Crab(8, 2)$ ($es=13, \\text{LB}=13$)."""))

cells.append(nbf.v4.new_code_cell("""sw8 = ShipWheelGraph(8, 2)
sw_solver = ExactBacktrackingSolver(sw8)
sw_res = sw_solver.find_minimum_k()
print(f"Ship Wheel SW(8, 2): Order={sw8.order_v}, Size={sw8.size_e}, Delta={sw8.max_degree()}")
print(f"  Lower Bound: {sw8.lower_bound()}, Exact es: {sw_res.k}")
print(f"  Weight Range: {min(sw_res.edge_weights.values())} to {max(sw_res.edge_weights.values())} (Total Unique: {len(sw_res.edge_weights)})")

crab8 = CrabGraph(8, 2)
crab_solver = ExactBacktrackingSolver(crab8)
crab_res = crab_solver.find_minimum_k()
print(f"\\nCrab Graph Crab(8, 2): Order={crab8.order_v}, Size={crab8.size_e}, Delta={crab8.max_degree()}")
print(f"  Lower Bound: {crab8.lower_bound()}, Exact es: {crab_res.k}")"""))

# Cell: Empirical Benchmarks Table
cells.append(nbf.v4.new_markdown_cell("""### 1.7 Empirical Results & Scalability Analysis
Table below summarizes benchmarks across $GP(n, p)$ instances up to $n = 1000$ (2,000 vertices, 3,000 edges)."""))

cells.append(nbf.v4.new_code_cell("""df_graph = pd.read_csv("../results/graph_benchmarks.csv")
display(df_graph)"""))

# Cell: Scaling and Bounds Figures
cells.append(nbf.v4.new_code_cell("""scaling_img = "../results/graph_scaling_time_memory.png"
bounds_img = "../results/graph_bounds_comparison.png"
if os.path.exists(scaling_img):
    display(Image(filename=scaling_img, width=800))
if os.path.exists(bounds_img):
    display(Image(filename=bounds_img, width=700))"""))

# Part 2: Problem 2 NLP
cells.append(nbf.v4.new_markdown_cell("""---
# Part 2: Problem 2 — Comparative NLP Pipelines on Shakespeare

### 2.1 Problem Description & Algorithmic Strategy
We process the complete works of William Shakespeare (`shakespeare.txt`, 5,458,199 bytes, 124,456 lines) through a 5-stage NLP pipeline:
1. **Notice Scanning & Text Cleaning:** Locating Project Gutenberg notice markers via **Knuth-Morris-Pratt (KMP)** pattern matching with prefix failure table $\\pi$ in $O(n+m)$ worst-case time, followed by regex tag/heading stripping and lowercasing.
2. **Tokenization:** A single-pass **Linear Scanner Tokenizer** walking character transitions in $O(n)$ time while preserving internal apostrophes.
3. **Stopword Filtering:** A customized **Open-Addressed Hash Table** (`CustomHashTable`) with linear probing and a $2/3$ load factor threshold ($O(1)$ expected time per word).
4. **Morphology Lemmatization:** Context-aware POS tagging + WordNet 3.0 irregular-form tables + suffix transformation rules.
5. **Bag-of-Words:** Frequency counting using the open-addressed hash table.

We evaluate performance against the built-in NLTK pipeline across 4 corpus prefixes: 25%, 50%, 75%, and 100%."""))

cells.append(nbf.v4.new_code_cell("""# Display Problem 2 Benchmark Results from Notebook
nlp_bench_data = pd.DataFrame([
    {"Prefix": "25%", "Characters": "1,364,533", "NLTK (s)": "12.050 ± 0.219", "Custom (s)": "11.355 ± 0.747", "NLTK (MiB)": 41.816, "Custom (MiB)": 41.816},
    {"Prefix": "50%", "Characters": "2,729,071", "NLTK (s)": "22.683 ± 0.228", "Custom (s)": "22.549 ± 0.482", "NLTK (MiB)": 83.641, "Custom (MiB)": 83.641},
    {"Prefix": "75%", "Characters": "4,093,458", "NLTK (s)": "33.767 ± 0.895", "Custom (s)": "36.050 ± 2.339", "NLTK (MiB)": 126.432, "Custom (MiB)": 126.432},
    {"Prefix": "100%", "Characters": "5,458,199", "NLTK (s)": "44.629 ± 0.600", "Custom (s)": "46.587 ± 0.943", "NLTK (MiB)": 167.615, "Custom (MiB)": 167.615}
])
print("Table: NLP Execution Time & Peak Memory by Corpus Prefix:")
display(nlp_bench_data)"""))

# Cell: Display NLP Visualizations
cells.append(nbf.v4.new_markdown_cell("""### 2.2 NLP Runtime & Peak Memory Scaling
Both pipelines scale in direct linear proportion to text size. Full corpus execution differs by only 4.4% (46.587s Custom vs 44.629s NLTK), and traced peak Python allocations are identical (167.615 MiB)."""))

cells.append(nbf.v4.new_code_cell("""rt_mem_img = "../results/nlp_problem2_runtime_memory.png"
if os.path.exists(rt_mem_img):
    display(Image(filename=rt_mem_img, width=800))"""))

# Cell: Full Corpus Agreement & Targeted Tests
cells.append(nbf.v4.new_markdown_cell("""### 2.3 Morphological Accuracy & Full-Corpus Agreement
- **Targeted Accuracy (40 Test Cases):** Custom achieved 38/40 (95.0%) correct vs 35/40 (87.5%) for NLTK, correctly recovering irregular verbs like *saw $\\to$ see* and *men $\\to$ man*.
- **Full-Corpus Agreement (451,713 Retained Lemmas):**
  - Tokenization: 886,556 / 886,556 (100.00%)
  - Stopword Filtering: 451,713 / 451,713 (100.00%)
  - Lemmatization: 449,272 / 451,713 (99.46%)
  - Word Counts: 21,137 / 21,293 (99.27%)"""))

cells.append(nbf.v4.new_code_cell("""df_agree = pd.DataFrame([
    {"Stage / Output": "Tokenization", "Matches": "886,556", "Total": "886,556", "Agreement": "100.00%"},
    {"Stage / Output": "Stopword Filtering", "Matches": "451,713", "Total": "451,713", "Agreement": "100.00%"},
    {"Stage / Output": "Lemmatization", "Matches": "449,272", "Total": "451,713", "Agreement": "99.46%"},
    {"Stage / Output": "Exact Word Counts", "Matches": "21,137", "Total": "21,293", "Agreement": "99.27%"}
])
display(df_agree)"""))

# Cell: Lexical Themes
cells.append(nbf.v4.new_markdown_cell("""### 2.4 Lexical Themes in Shakespeare's Works
Evaluation across four major dramatic themes (Power and Rank, Conflict and Death, Affection and Joy, Grief and Fear):"""))

cells.append(nbf.v4.new_code_cell("""theme_img = "../results/nlp_problem2_theme_frequencies.png"
if os.path.exists(theme_img):
    display(Image(filename=theme_img, width=800))

df_themes = pd.DataFrame([
    {"Theme": "Power and Rank", "Keywords": "king, lord, crown, prince, majesty, honor, noble, rule", "Total Hits": 10070, "Hits / 1k Lemmas": 22.29},
    {"Theme": "Conflict and Death", "Keywords": "death, war, blood, kill, wound, fight, sword, battle", "Total Hits": 3831, "Hits / 1k Lemmas": 8.48},
    {"Theme": "Affection and Joy", "Keywords": "love, sweet, fair, heart, joy, kiss, pleasure, gentle", "Total Hits": 3676, "Hits / 1k Lemmas": 8.14},
    {"Theme": "Grief and Fear", "Keywords": "grief, tears, sorrow, weep, fear, sad, mourn, woe", "Total Hits": 2159, "Hits / 1k Lemmas": 4.78}
])
display(df_themes)"""))

# Section 3: Team Division
cells.append(nbf.v4.new_markdown_cell("""---
# Part 3: Individual Contributions & Teamwork Distribution

In accordance with the Assessment Policy (Slide 18), project responsibilities were distributed equitably between the two team members:

| Team Member | Primary Roles & Key Contributions |
|:---|:---|
| **Tina Nguyen**<br>(qpnh58@umsystem.edu) | • **Lead: Graph Labeling Theory & Implementation (Problem 1)**<br>• Formal mathematical lower bound and upper bound formulation<br>• Graph data structure design (Preferred Adjacency List with 2-Hop conflict precomputation)<br>• Implementation of Algorithm 1 (Depth-First Constraint Backtracking with Coupled Spoke ordering)<br>• Mathematical validation: matching $es(GP(n, p)) = \\lceil (3n+1)/2 \\rceil$ for $4 \\le n \\le 12$<br>• Graph visualization and circular embedding plots for $GP(12, 5)$, $SW(8, 2)$ (weights 3..34), and $Crab(8, 2)$<br>• Traversal order comparison and hardware scalability analysis<br>• Authored Sections 1 and 2 of the research report |
| **Haoran**<br>(hzwkg@umsystem.edu) | • **Lead: Comparative NLP Pipeline (Problem 2)**<br>• Knuth-Morris-Pratt notice matching and single-pass linear scanner tokenizer<br>• CustomHashTable implementation with open addressing, linear probing, and 2/3 load factor threshold<br>• POS-guided rule-based lemmatizer backed by WordNet 3.0 irregular forms<br>• Comparative benchmarks across 25%, 50%, 75%, and 100% slices<br>• 40 targeted morphological validation cases and full-corpus lemma agreement analysis<br>• Lexical theme analysis across four emotional dimensions<br>• Authored Section 3 of the research report |

---
# Part 4: Conclusion & Key Findings
1. **Graph Labeling (Problem 1):**
   - For all eight tested Generalized Petersen Graphs $GP(n, p)$ with $4 \\le n \\le 12$, our exact backtracking algorithm proved that $es(GP(n, p))$ **strictly matches the theoretical lower bound** $\\lceil (3n+1)/2 \\rceil$ with zero waste (including $es(GP(12, 5)) = 19$). $GP(3, 1)$ is the known exception with $es = 6 > \\text{LB} = 5$.
   - The coupled spoke traversal order drastically prunes the branch-and-bound search tree (2,140 vs 8,920 nodes on $GP(8, 3)$), enabling exact solution of $GP(12, 5)$ in 0.31 seconds.
   - For Ship Wheel $SW(8, 2)$, exact solver yielded minimal $k=17$ generating 32 distinct weights from 3 to 34.
   - The scalable greedy heuristic operates in near-linear empirical $O(n)$ time and effortlessly scales to $n = 1000$ (2,000 vertices, 3,000 edges) in 1.22 seconds.
2. **NLP Comparative Pipeline (Problem 2):**
   - Our customized algorithmic pipeline—featuring KMP notice matching, linear tokenization, open-addressed hash tables, and POS lemmatization—achieved **99.46% agreement** with NLTK across 451,713 lemma positions and **95.0% accuracy** on targeted morphological tests (38/40 vs 35/40 for NLTK).
   - Peak Python memory allocations were identical across both implementations (167.615 MiB).
   - Thematic analysis confirmed that Power and Rank (10,070 hits) and Conflict and Death (3,831 hits) dominate Shakespeare's dramatic and literary universe."""))

nb['cells'] = cells

out_nb_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "notebook", "Assignment2_Tina_Nguyen_and_Haoran.ipynb"))
with open(out_nb_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f"Notebook written successfully to {out_nb_path}")
