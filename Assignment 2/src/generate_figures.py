"""
CS-5592: Design and Analysis of Algorithms - Assignment 2
Generate Figures and Benchmark Tables
Authors: Tina Nguyen (qpnh58@umsystem.edu) & Haoran (hzwkg@umsystem.edu)
Affiliation: University of Missouri - Kansas City (UMKC)
"""

import os
import sys
import math
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx

# Add src to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from graph_labeling import (
    GeneralizedPetersenGraph, ShipWheelGraph, CrabGraph,
    ExactBacktrackingSolver, ScalableHeuristicSolver, benchmark_graph_labeling,
    export_labeling_details
)
from nlp_pipeline import (
    CustomNLP_Pipeline, BuiltinNLTK_Pipeline, ShakespeareMoodAnalyzer,
    run_comparative_benchmark
)

RESULTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results"))
os.makedirs(RESULTS_DIR, exist_ok=True)


def plot_labeled_gp_graph(n: int, p: int, filename: str):
    """Draws a circular layout of GP(n, p) with vertex labels and legible edge weights."""
    gp = GeneralizedPetersenGraph(n, p)
    # Solve exactly if small, else heuristic
    if n <= 12:
        solver = ExactBacktrackingSolver(gp, timeout_per_k=5.0)
        res = solver.find_minimum_k(max_k_offset=2)
    else:
        solver = ScalableHeuristicSolver(gp)
        res = solver.solve()

    labels = res.labels
    k = res.k

    G = nx.Graph()
    for i in range(2 * n):
        G.add_node(i)
    for u, v in gp.edges:
        G.add_edge(u, v, weight=labels[u] + labels[v])

    pos = {}
    R_out = 2.2
    for i in range(n):
        angle = 2 * math.pi * i / n + math.pi / 2
        pos[i] = (R_out * math.cos(angle), R_out * math.sin(angle))
    R_in = 1.15
    for i in range(n):
        angle = 2 * math.pi * i / n + math.pi / 2
        pos[n + i] = (R_in * math.cos(angle), R_in * math.sin(angle))

    fig, ax = plt.subplots(figsize=(10, 10))
    status_label = "Exact Optimal es(G)" if res.is_exact_minimal else f"Feasible Labeling k"
    ax.set_title(f"Edge Irregular Vertex {k}-Labeling of GP({n}, {p})\n"
                 f"|V|={gp.num_vertices}, |E|={gp.num_edges}, {status_label}={k} (Theoretical Lower Bound={gp.lower_bound_es()})",
                 fontsize=13, fontweight='bold', pad=15)

    # Draw nodes: Outer nodes in cyan, inner nodes in coral
    node_colors = ['#4DA8DA' if i < n else '#F38181' for i in range(2 * n)]
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=680, edgecolors='#1B262C', linewidths=1.5, ax=ax)

    # Node labels: vertex label
    node_labels = {i: f"{labels[i]}" for i in range(2 * n)}
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10.5, font_weight='bold', font_color='#111111', ax=ax)

    # Draw edges: outer cycle, spokes, inner star
    outer_edges = [(i, (i + 1) % n) for i in range(n)]
    spoke_edges = [(i, n + i) for i in range(n)]
    inner_edges = [(n + i, n + ((i + p) % n)) for i in range(n)]

    nx.draw_networkx_edges(G, pos, edgelist=outer_edges, edge_color='#2B580C', width=2.0, ax=ax, label="Outer Cycle")
    nx.draw_networkx_edges(G, pos, edgelist=spoke_edges, edge_color='#637373', width=1.8, style='dashed', ax=ax, label="Spokes")
    nx.draw_networkx_edges(G, pos, edgelist=inner_edges, edge_color='#D72323', width=2.0, ax=ax, label="Inner Star")

    # Edge labels: draw outer/spoke at midpoint (0.5), and inner star at 0.25 to avoid center crowding
    outer_labels = {(u, v): str(G[u][v]['weight']) for u, v in outer_edges}
    spoke_labels = {(u, v): str(G[u][v]['weight']) for u, v in spoke_edges}
    inner_labels = {(u, v): str(G[u][v]['weight']) for u, v in inner_edges}

    nx.draw_networkx_edge_labels(G, pos, edge_labels=outer_labels, label_pos=0.5, font_size=8, font_color='#000080',
                                 bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.9), ax=ax)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=spoke_labels, label_pos=0.5, font_size=8, font_color='#333333',
                                 bbox=dict(boxstyle="round,pad=0.12", fc="#F0F0F0", ec="none", alpha=0.9), ax=ax)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=inner_labels, label_pos=0.25, font_size=7.5, font_color='#8B0000',
                                 bbox=dict(boxstyle="round,pad=0.12", fc="#FFF0F0", ec="none", alpha=0.9), ax=ax)

    ax.legend(loc="upper right", frameon=True, fontsize=10)
    ax.axis('off')
    plt.tight_layout()
    out_path = os.path.join(RESULTS_DIR, filename)
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_path}")


def plot_ship_wheel_graph(filename: str = "ship_wheel_visualization.png"):
    """Draws labeled Ship Wheel SW(8, 2) matching Slide 15."""
    sw = ShipWheelGraph(8, 2)
    solver = ExactBacktrackingSolver(sw, timeout_per_k=30.0)
    res = solver.find_minimum_k(max_k_offset=5)
    if not res.is_valid:
        solver = ScalableHeuristicSolver(sw)
        res = solver.solve()
    labels = res.labels
    k = res.k

    G = nx.Graph()
    for i in range(sw.num_vertices):
        G.add_node(i)
    for u, v in sw.edges:
        G.add_edge(u, v, weight=labels[u] + labels[v])

    pos = {}
    pos[0] = (0.0, 0.0)  # Hub
    R_rim = 1.8
    for i in range(1, 9):
        angle = 2 * math.pi * (i - 1) / 8 + math.pi / 2
        pos[i] = (R_rim * math.cos(angle), R_rim * math.sin(angle))
    R_leaf = 2.8
    leaf_idx = 9
    for i in range(1, 9):
        base_angle = 2 * math.pi * (i - 1) / 8 + math.pi / 2
        pos[leaf_idx] = (R_leaf * math.cos(base_angle - 0.15), R_leaf * math.sin(base_angle - 0.15))
        pos[leaf_idx + 1] = (R_leaf * math.cos(base_angle + 0.15), R_leaf * math.sin(base_angle + 0.15))
        leaf_idx += 2

    fig, ax = plt.subplots(figsize=(10, 10))
    min_w = min(res.edge_weights)
    max_w = max(res.edge_weights)
    ax.set_title(f"Vertex k-Labeling of Ship Wheel Graph SW(8, 2)\n"
                 f"|V|={sw.num_vertices}, |E|={sw.num_edges}, k={k} (Lower Bound={sw.lower_bound_es()}, Weights: {min_w}..{max_w})",
                 fontsize=13, fontweight='bold', pad=15)

    colors = ['#FFD460'] + ['#00ADB5'] * 8 + ['#EA5455'] * 16
    nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=550, edgecolors='#222831', linewidths=1.5, ax=ax)
    node_labels = {i: str(labels[i]) for i in range(sw.num_vertices)}
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=9.5, font_weight='bold', ax=ax)
    nx.draw_networkx_edges(G, pos, edge_color='#393E46', width=1.5, alpha=0.8, ax=ax)

    edge_labels = {(u, v): str(d['weight']) for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7, font_color='#1B262C',
                                 bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.8), ax=ax)

    ax.axis('off')
    plt.tight_layout()
    out_path = os.path.join(RESULTS_DIR, filename)
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_path}")


def plot_crab_graph(filename: str = "crab_visualization.png"):
    """Draws labeled Crab Graph Crab(4, 2) proving optimal vertex k-labeling."""
    crab = CrabGraph(4, 2)
    solver = ExactBacktrackingSolver(crab, timeout_per_k=10.0)
    res = solver.find_minimum_k(max_k_offset=5)
    labels = res.labels
    k = res.k

    G = nx.Graph()
    for i in range(crab.num_vertices):
        G.add_node(i)
    for u, v in crab.edges:
        G.add_edge(u, v, weight=labels[u] + labels[v])

    pos = {}
    pos[0] = (0.0, 0.0)  # Head
    for i in range(1, 5):
        angle = 2 * math.pi * (i - 1) / 4 + math.pi / 4
        pos[i] = (1.8 * math.cos(angle), 1.8 * math.sin(angle))
    leaf_idx = 5
    for i in range(1, 5):
        base_angle = 2 * math.pi * (i - 1) / 4 + math.pi / 4
        pos[leaf_idx] = (2.8 * math.cos(base_angle - 0.2), 2.8 * math.sin(base_angle - 0.2))
        pos[leaf_idx + 1] = (2.8 * math.cos(base_angle + 0.2), 2.8 * math.sin(base_angle + 0.2))
        leaf_idx += 2

    fig, ax = plt.subplots(figsize=(8, 8))
    min_w = min(res.edge_weights)
    max_w = max(res.edge_weights)
    ax.set_title(f"Vertex k-Labeling of Crab Graph Crab(4, 2)\n"
                 f"|V|={crab.num_vertices}, |E|={crab.num_edges}, k={k} (Lower Bound={crab.lower_bound_es()}, Weights: {min_w}..{max_w})",
                 fontsize=12, fontweight='bold', pad=15)

    colors = ['#FFD460'] + ['#00ADB5'] * 4 + ['#EA5455'] * 8
    nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=550, edgecolors='#222831', linewidths=1.5, ax=ax)
    node_labels = {i: str(labels[i]) for i in range(crab.num_vertices)}
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=9.5, font_weight='bold', ax=ax)
    nx.draw_networkx_edges(G, pos, edge_color='#393E46', width=1.5, alpha=0.8, ax=ax)

    edge_labels = {(u, v): str(d['weight']) for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7.5, font_color='#1B262C',
                                 bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.8), ax=ax)

    ax.axis('off')
    plt.tight_layout()
    out_path = os.path.join(RESULTS_DIR, filename)
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_path}")


def generate_graph_benchmark_plots_and_csv():
    """Benchmarks GP(n, p) and saves plots & CSV."""
    records = benchmark_graph_labeling()
    df = pd.DataFrame(records)
    csv_path = os.path.join(RESULTS_DIR, "graph_benchmarks.csv")
    df.to_csv(csv_path, index=False)
    print(f"Saved: {csv_path}")

    # Plot 1: Runtime & Memory Scaling
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    orders = df['Order_V'].values
    heur_times = df['Heuristic_Time_s'].values
    heur_mems = df['Heuristic_Memory_KB'].values

    ax1.plot(orders, heur_times, 'o-', color='#1F77B4', linewidth=2, markersize=6, label="Greedy Constructive T(s)")
    # Filter exact times where a numerical time was recorded
    exact_mask = df['Exact_Time_s'] != '-'
    if exact_mask.any():
        ax1.plot(df.loc[exact_mask, 'Order_V'], df.loc[exact_mask, 'Exact_Time_s'].astype(float),
                 's--', color='#D62728', linewidth=2, markersize=6, label="Exact Backtracking T(s)")

    ax1.set_xlabel("Order |V| = 2n", fontsize=12, fontweight='bold')
    ax1.set_ylabel("Execution Time (seconds)", fontsize=12, fontweight='bold')
    ax1.set_title("Observed Runtime vs Graph Order (Empirical Scaling)", fontsize=12, fontweight='bold')
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.grid(True, which="both", ls="--", alpha=0.6)
    ax1.legend(fontsize=10)

    # Plot Memory
    ax2.plot(orders, heur_mems, '^-', color='#2CA02C', linewidth=2, markersize=6, label="Solver Peak Memory (KB)")
    ax2.set_xlabel("Order |V| = 2n", fontsize=12, fontweight='bold')
    ax2.set_ylabel("Peak Memory (KB)", fontsize=12, fontweight='bold')
    ax2.set_title("Memory Consumption Scaling (Solver Heap Overhead)", fontsize=12, fontweight='bold')
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.grid(True, which="both", ls="--", alpha=0.6)
    ax2.legend(fontsize=10)

    plt.tight_layout()
    out_plot1 = os.path.join(RESULTS_DIR, "graph_scaling_time_memory.png")
    plt.savefig(out_plot1, dpi=300)
    plt.close()
    print(f"Saved: {out_plot1}")

    # Plot 2: Algorithmic k vs Theoretical Bounds
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(orders, df['Lower_Bound'], 'g^-', linewidth=2.5, markersize=7, label=r"Theoretical Lower Bound: $\max(\lceil(|E|+1)/2\rceil, \Delta)$")
    ax.plot(orders, df['Heuristic_k'], 'bo--', linewidth=2.0, markersize=6, label=r"Greedy Heuristic Result $k$")

    # Exact optimal vs feasible upper bound where available
    opt_mask = df['Exact_Status'] == 'OPTIMAL'
    if opt_mask.any():
        ax.plot(df.loc[opt_mask, 'Order_V'], df.loc[opt_mask, 'Exact_k'].astype(int),
                'r*', markersize=10, label=r"Exact Proven $es(G)$ (Backtracking)")

    feas_mask = df['Exact_Status'] == 'FEASIBLE'
    if feas_mask.any():
        feas_k = [int(str(v).split()[0]) for v in df.loc[feas_mask, 'Exact_k']]
        ax.plot(df.loc[feas_mask, 'Order_V'], feas_k,
                's', color='#FF7F0E', markersize=7, label=r"Exact Solver Feasible Upper Bound")

    ax.plot(orders, df['Upper_Bound_Log'], 'm:', linewidth=2.0, label=r"Asim Log Reference Curve: $|E|\log_2 |V|$ (Circulant Reference)")

    ax.set_xlabel("Order |V| = 2n", fontsize=12, fontweight='bold')
    ax.set_ylabel("Label Value k", fontsize=12, fontweight='bold')
    ax.set_title(r"Vertex $k$-Labeling: Algorithmic Results vs Theoretical Bounds", fontsize=13, fontweight='bold')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.grid(True, which="both", ls="--", alpha=0.6)
    ax.legend(fontsize=10.5)

    plt.tight_layout()
    out_plot2 = os.path.join(RESULTS_DIR, "graph_bounds_comparison.png")
    plt.savefig(out_plot2, dpi=300)
    plt.close()
    print(f"Saved: {out_plot2}")


def generate_nlp_benchmark_plots_and_csv():
    """Benchmarks NLP pipeline and generates figures and CSV tables."""
    shakespeare_path = os.path.join(os.path.dirname(__file__), "..", "docs", "shakespeare.txt")
    records = run_comparative_benchmark(shakespeare_path)
    df = pd.DataFrame(records)
    csv_path = os.path.join(RESULTS_DIR, "nlp_benchmarks.csv")
    df.to_csv(csv_path, index=False)
    print(f"Saved: {csv_path}")

    fractions = df['Fraction'].values
    custom_times = df['Custom_Total_Time_s'].values
    nltk_times = df['NLTK_Total_Time_s'].values
    custom_mems = df['Custom_Peak_Mem_MB'].values
    nltk_mems = df['NLTK_Peak_Mem_MB'].values

    # Runtime & Memory comparison plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    x = np.arange(len(fractions))
    width = 0.35

    ax1.bar(x - width/2, custom_times, width, label='Custom Pipeline', color='#2B580C', edgecolor='black')
    ax1.bar(x + width/2, nltk_times, width, label='Built-in NLTK Pipeline', color='#D72323', edgecolor='black')
    ax1.set_xlabel('Corpus Fraction', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Total Execution Time (seconds)', fontsize=12, fontweight='bold')
    ax1.set_title('NLP Execution Time Comparison: Custom vs. NLTK', fontsize=13, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(fractions, fontsize=10, fontweight='bold')
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    ax1.legend(fontsize=10)

    for i in range(len(fractions)):
        ax1.text(x[i] - width/2, custom_times[i] + 0.1, f"{custom_times[i]:.2f}s", ha='center', va='bottom', fontsize=9, fontweight='bold')
        ax1.text(x[i] + width/2, nltk_times[i] + 0.1, f"{nltk_times[i]:.2f}s", ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax2.bar(x - width/2, custom_mems, width, label='Custom Peak Memory', color='#118AB2', edgecolor='black')
    ax2.bar(x + width/2, nltk_mems, width, label='NLTK Peak Memory', color='#FFD166', edgecolor='black')
    ax2.set_xlabel('Corpus Fraction', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Peak Memory Consumption (MB)', fontsize=12, fontweight='bold')
    ax2.set_title('NLP Peak Memory Consumption Comparison', fontsize=13, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(fractions, fontsize=10, fontweight='bold')
    ax2.grid(axis='y', linestyle='--', alpha=0.7)
    ax2.legend(fontsize=10)

    for i in range(len(fractions)):
        ax2.text(x[i] - width/2, custom_mems[i] + 1, f"{custom_mems[i]:.1f}M", ha='center', va='bottom', fontsize=9)
        ax2.text(x[i] + width/2, nltk_mems[i] + 1, f"{nltk_mems[i]:.1f}M", ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    out_nlp_plot1 = os.path.join(RESULTS_DIR, "nlp_runtime_memory_comparison.png")
    plt.savefig(out_nlp_plot1, dpi=300)
    plt.close()
    print(f"Saved: {out_nlp_plot1}")

    # Stage breakdown plot
    fig, ax = plt.subplots(figsize=(10, 5))
    stages = ['Clean & Tokenize', 'Stemming', 'Bag of Words']
    custom_stages = [
        df['Custom_Time_Clean'].iloc[-1] + df['Custom_Time_Tok'].iloc[-1],
        df['Custom_Time_Stem'].iloc[-1],
        df['Custom_Time_BoW'].iloc[-1]
    ]
    nltk_stages = [
        df['NLTK_Time_Clean'].iloc[-1] + df['NLTK_Time_Tok'].iloc[-1],
        df['NLTK_Time_Stem'].iloc[-1],
        df['NLTK_Time_BoW'].iloc[-1]
    ]

    x_s = np.arange(len(stages))
    ax.bar(x_s - width/2, custom_stages, width, label='Custom Pipeline (Full Corpus)', color='#06D6A0', edgecolor='black')
    ax.bar(x_s + width/2, nltk_stages, width, label='NLTK Pipeline (Full Corpus)', color='#EF476F', edgecolor='black')
    ax.set_ylabel('Time (seconds)', fontsize=12, fontweight='bold')
    ax.set_title('Stage-by-Stage NLP Runtime Breakdown (100% Corpus)', fontsize=13, fontweight='bold')
    ax.set_xticks(x_s)
    ax.set_xticklabels(stages, fontsize=11, fontweight='bold')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.legend(fontsize=10)

    for i in range(len(stages)):
        ax.text(x_s[i] - width/2, custom_stages[i] + 0.05, f"{custom_stages[i]:.2f}s", ha='center', va='bottom', fontsize=9.5, fontweight='bold')
        ax.text(x_s[i] + width/2, nltk_stages[i] + 0.05, f"{nltk_stages[i]:.2f}s", ha='center', va='bottom', fontsize=9.5, fontweight='bold')

    plt.tight_layout()
    out_stage_plot = os.path.join(RESULTS_DIR, "nlp_stage_breakdown.png")
    plt.savefig(out_stage_plot, dpi=300)
    plt.close()
    print(f"Saved: {out_stage_plot}")

    # Top words & Mood plot
    with open(shakespeare_path, 'r', encoding='utf-8') as f:
        full_text = f.read()
    pipe = CustomNLP_Pipeline()
    res = pipe.run_pipeline(full_text)
    bow = res["bow"]

    # Top 15 content words
    sorted_words = sorted(bow.items(), key=lambda x: x[1], reverse=True)[:15]
    df_top15 = pd.DataFrame(sorted_words, columns=['Word', 'Frequency'])
    df_top15.to_csv(os.path.join(RESULTS_DIR, "shakespeare_top_words.csv"), index=False)

    # Mood analysis
    mood_res = ShakespeareMoodAnalyzer.analyze_mood(bow)
    mood_rows = []
    for theme, data in mood_res.items():
        rep = ", ".join([f"{t} ({c})" for t, c in data["top_terms"][:4]])
        mood_rows.append({
            "Theme": theme,
            "Total_Occurrences": data["count"],
            "Corpus_Thematic_Share_Pct": data["percentage"],
            "Representative_Terms": rep
        })
    df_mood = pd.DataFrame(mood_rows)
    df_mood.to_csv(os.path.join(RESULTS_DIR, "shakespeare_mood_analysis.csv"), index=False)

    # Plot BoW Top 15
    fig, ax = plt.subplots(figsize=(10, 6))
    words = df_top15['Word'].values[::-1]
    counts = df_top15['Frequency'].values[::-1]
    bars = ax.barh(words, counts, color='#1F77B4', edgecolor='black', height=0.65)
    ax.set_xlabel('Word Occurrence Frequency', fontsize=12, fontweight='bold')
    ax.set_title("Top 15 Most Frequent Content Words in Shakespeare's Works", fontsize=13, fontweight='bold')
    ax.grid(axis='x', linestyle='--', alpha=0.7)
    for bar in bars:
        w = bar.get_width()
        ax.text(w + 25, bar.get_y() + bar.get_height()/2, f"{int(w):,}", ha='left', va='center', fontsize=9, fontweight='bold')
    ax.set_xlim(0, max(counts) * 1.15)
    plt.tight_layout()
    out_bow_plot = os.path.join(RESULTS_DIR, "nlp_top_words_bow.png")
    plt.savefig(out_bow_plot, dpi=300)
    plt.close()
    print(f"Saved: {out_bow_plot}")

    # Plot Mood
    fig, ax = plt.subplots(figsize=(10, 5))
    themes = df_mood['Theme'].values
    shares = df_mood['Corpus_Thematic_Share_Pct'].values
    colors = ['#FFD166', '#EF476F', '#06D6A0', '#118AB2', '#073B4C', '#7209B7']
    bars = ax.bar(themes, shares, color=colors, edgecolor='black', width=0.55)
    ax.set_ylabel('Thematic Category Share (%)', fontsize=12, fontweight='bold')
    ax.set_title("Thematic Sentiment & Mood Distribution in Shakespeare's Works", fontsize=13, fontweight='bold')
    ax.set_xticks(np.arange(len(themes)))
    ax.set_xticklabels(themes, rotation=20, ha='right', fontsize=10, fontweight='bold')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 0.5, f"{h:.1f}%", ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax.set_ylim(0, max(shares) * 1.2)
    plt.tight_layout()
    out_mood_plot = os.path.join(RESULTS_DIR, "nlp_mood_distribution.png")
    plt.savefig(out_mood_plot, dpi=300)
    plt.close()
    print(f"Saved: {out_mood_plot}")


if __name__ == "__main__":
    print("Generating Graph Visualizations...")
    plot_labeled_gp_graph(5, 2, "gp5_2_labeling_visualization.png")
    plot_labeled_gp_graph(12, 5, "gp12_5_labeling_visualization.png")
    plot_ship_wheel_graph("ship_wheel_visualization.png")
    plot_crab_graph("crab_visualization.png")

    print("\nGenerating Graph Benchmarks and Scaling Plots...")
    generate_graph_benchmark_plots_and_csv()

    print("\nGenerating NLP Benchmarks, BoW, and Mood Plots...")
    generate_nlp_benchmark_plots_and_csv()

    print("\nAll figures and results generated successfully!")
