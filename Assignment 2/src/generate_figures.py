"""
CS-5592: Design and Analysis of Algorithms - Assignment 2
Generate Figures and Benchmark Tables
Authors: Tina Nguyen & Haoran
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
    ExactBacktrackingSolver, ScalableHeuristicSolver, benchmark_graph_labeling
)
from nlp_pipeline import (
    CustomNLP_Pipeline, BuiltinNLTK_Pipeline, ShakespeareMoodAnalyzer,
    run_comparative_benchmark
)

RESULTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results"))
os.makedirs(RESULTS_DIR, exist_ok=True)


def plot_labeled_gp_graph(n: int, p: int, filename: str):
    """Draws a circular layout of GP(n, p) with vertex labels and edge weights."""
    gp = GeneralizedPetersenGraph(n, p)
    # Solve exactly if small, else heuristic
    if n <= 12:
        solver = ExactBacktrackingSolver(gp, timeout_per_k=2.0)
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
    # Outer circle: radius R_out
    R_out = 2.0
    for i in range(n):
        angle = 2 * math.pi * i / n + math.pi / 2
        pos[i] = (R_out * math.cos(angle), R_out * math.sin(angle))
    # Inner circle: radius R_in
    R_in = 1.0
    for i in range(n):
        angle = 2 * math.pi * i / n + math.pi / 2
        pos[n + i] = (R_in * math.cos(angle), R_in * math.sin(angle))

    fig, ax = plt.subplots(figsize=(9, 9))
    ax.set_title(f"Edge Irregular Vertex {k}-Labeling of GP({n}, {p})\n"
                 f"|V|={gp.num_vertices}, |E|={gp.num_edges}, es(G)={k} (Lower Bound={gp.lower_bound_es()})",
                 fontsize=14, fontweight='bold', pad=15)

    # Draw nodes
    # Outer nodes in cyan, inner nodes in orange
    node_colors = ['#4DA8DA' if i < n else '#F38181' for i in range(2 * n)]
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=650, edgecolors='#1B262C', linewidths=1.5, ax=ax)

    # Node labels: show vertex label value
    node_labels = {i: f"{labels[i]}" for i in range(2 * n)}
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=11, font_weight='bold', font_color='#111111', ax=ax)

    # Draw edges
    # Distinguish outer, spoke, inner edges
    outer_edges = [(i, (i + 1) % n) for i in range(n)]
    spoke_edges = [(i, n + i) for i in range(n)]
    inner_edges = [(n + i, n + ((i + p) % n)) for i in range(n)]

    nx.draw_networkx_edges(G, pos, edgelist=outer_edges, edge_color='#2B580C', width=2.0, ax=ax, label="Outer Cycle")
    nx.draw_networkx_edges(G, pos, edgelist=spoke_edges, edge_color='#637373', width=1.8, style='dashed', ax=ax, label="Spokes")
    nx.draw_networkx_edges(G, pos, edgelist=inner_edges, edge_color='#D72323', width=2.0, ax=ax, label="Inner Star")

    # Edge labels: edge weights
    edge_labels = {(u, v): str(d['weight']) for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, font_color='#000080',
                                 bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85), ax=ax)

    ax.legend(loc="upper right", frameon=True)
    ax.axis('off')
    plt.tight_layout()
    out_path = os.path.join(RESULTS_DIR, filename)
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_path}")


def plot_ship_wheel_graph(filename: str = "ship_wheel_visualization.png"):
    """Draws labeled Ship Wheel SW(8, 2) matching Slide 15."""
    sw = ShipWheelGraph(8, 2)
    solver = ScalableHeuristicSolver(sw)
    res = solver.solve(max_restarts=10)
    labels = res.labels
    k = res.k

    G = nx.Graph()
    for i in range(sw.num_vertices):
        G.add_node(i)
    for u, v in sw.edges:
        G.add_edge(u, v, weight=labels[u] + labels[v])

    pos = {}
    pos[0] = (0.0, 0.0) # Hub
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
    ax.set_title(f"Vertex k-Labeling of Ship Wheel Graph SW(8, 2)\n"
                 f"|V|={sw.num_vertices}, |E|={sw.num_edges}, k={k} (Lower Bound={sw.lower_bound_es()})",
                 fontsize=14, fontweight='bold', pad=15)

    colors = ['#FFD460'] + ['#00ADB5'] * 8 + ['#EA5455'] * 16
    nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=550, edgecolors='#222831', linewidths=1.5, ax=ax)
    node_labels = {i: str(labels[i]) for i in range(sw.num_vertices)}
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10, font_weight='bold', ax=ax)
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

    ax1.plot(orders, heur_times, 'o-', color='#1F77B4', linewidth=2, markersize=6, label="Scalable Heuristic T(s)")
    # Filter exact times for n <= 16
    exact_mask = df['Exact_Time_s'] != '-'
    if exact_mask.any():
        ax1.plot(df.loc[exact_mask, 'Order_V'], df.loc[exact_mask, 'Exact_Time_s'].astype(float),
                 's--', color='#D62728', linewidth=2, markersize=6, label="Exact Backtracking T(s)")

    ax1.set_xlabel("Order |V| = 2n", fontsize=12, fontweight='bold')
    ax1.set_ylabel("Execution Time (seconds)", fontsize=12, fontweight='bold')
    ax1.set_title("Execution Time Complexity T(|V|, |E|)", fontsize=13, fontweight='bold')
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.grid(True, which="both", ls="--", alpha=0.6)
    ax1.legend(fontsize=10)

    # Plot Memory
    ax2.plot(orders, heur_mems, '^-', color='#2CA02C', linewidth=2, markersize=6, label="Peak Memory (KB)")
    ax2.set_xlabel("Order |V| = 2n", fontsize=12, fontweight='bold')
    ax2.set_ylabel("Peak Memory (KB)", fontsize=12, fontweight='bold')
    ax2.set_title("Memory Consumption Scaling", fontsize=13, fontweight='bold')
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
    ax.plot(orders, df['Heuristic_k'], 'bo--', linewidth=2.0, markersize=6, label=r"Algorithmic Result $k$ (Heuristic)")
    
    # Exact where available
    if exact_mask.any():
        ax.plot(df.loc[exact_mask, 'Order_V'], df.loc[exact_mask, 'Exact_k'].astype(int),
                'r*', markersize=10, label=r"Exact $es(G)$ (Backtracking)")

    ax.plot(orders, df['Upper_Bound_Log'], 'm:', linewidth=2.0, label=r"Asim Upper Bound: $|E|\log_2 |V|$")

    ax.set_xlabel("Order |V| = 2n", fontsize=12, fontweight='bold')
    ax.set_ylabel("Label Value k", fontsize=12, fontweight='bold')
    ax.set_title(r"Vertex $k$-Labeling: Algorithmic Results vs Theoretical Bounds", fontsize=13, fontweight='bold')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.grid(True, which="both", ls="--", alpha=0.6)
    ax.legend(fontsize=11)

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

    # Plot 1: Runtime Comparison across Slices
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    fractions = df['Fraction'].values
    custom_times = df['Custom_Total_Time_s'].values
    nltk_times = df['NLTK_Total_Time_s'].values

    x = np.arange(len(fractions))
    width = 0.35

    ax1.bar(x - width/2, custom_times, width, label='Custom Pipeline', color='#2B580C', edgecolor='black')
    ax1.bar(x + width/2, nltk_times, width, label='Built-in NLTK Pipeline', color='#D72323', edgecolor='black')
    ax1.set_xlabel('Corpus Fraction', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Total Execution Time (s)', fontsize=12, fontweight='bold')
    ax1.set_title('NLP Pipeline Execution Time Comparison T(n)', fontsize=13, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(fractions)
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    ax1.legend(fontsize=11)

    # Plot 2: Memory Consumption Comparison
    custom_mems = df['Custom_Peak_Mem_MB'].values
    nltk_mems = df['NLTK_Peak_Mem_MB'].values

    ax2.bar(x - width/2, custom_mems, width, label='Custom Pipeline', color='#1B262C', edgecolor='black')
    ax2.bar(x + width/2, nltk_mems, width, label='Built-in NLTK Pipeline', color='#0F4C81', edgecolor='black')
    ax2.set_xlabel('Corpus Fraction', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Peak Memory Consumption (MB)', fontsize=12, fontweight='bold')
    ax2.set_title('Peak Memory Consumption Comparison', fontsize=13, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(fractions)
    ax2.grid(axis='y', linestyle='--', alpha=0.7)
    ax2.legend(fontsize=11)

    plt.tight_layout()
    out_plot_runtime = os.path.join(RESULTS_DIR, "nlp_runtime_memory_comparison.png")
    plt.savefig(out_plot_runtime, dpi=300)
    plt.close()
    print(f"Saved: {out_plot_runtime}")

    # Plot 3: Stage Breakdown
    fig, ax = plt.subplots(figsize=(10, 5))
    stages = ['Clean Text', 'Tokenization', 'Stemming', 'Bag-of-Words']
    # 100% slice breakdown
    row100 = df.iloc[-1]
    custom_stages = [row100['Custom_Time_Clean'], row100['Custom_Time_Tok'], row100['Custom_Time_Stem'], row100['Custom_Time_BoW']]
    nltk_stages = [row100['NLTK_Time_Clean'], row100['NLTK_Time_Tok'], row100['NLTK_Time_Stem'], row100['NLTK_Time_BoW']]

    x_s = np.arange(len(stages))
    ax.bar(x_s - width/2, custom_stages, width, label='Custom Pipeline', color='#00ADB5', edgecolor='black')
    ax.bar(x_s + width/2, nltk_stages, width, label='NLTK Pipeline', color='#FF5722', edgecolor='black')
    ax.set_xlabel('Pipeline Stage', fontsize=12, fontweight='bold')
    ax.set_ylabel('Execution Time (seconds)', fontsize=12, fontweight='bold')
    ax.set_title('Per-Stage Execution Time on 100% Shakespeare Corpus (5.46 MB)', fontsize=13, fontweight='bold')
    ax.set_xticks(x_s)
    ax.set_xticklabels(stages, fontsize=11)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.legend(fontsize=11)

    plt.tight_layout()
    out_stage_plot = os.path.join(RESULTS_DIR, "nlp_stage_breakdown.png")
    plt.savefig(out_stage_plot, dpi=300)
    plt.close()
    print(f"Saved: {out_stage_plot}")

    # Top Words Analysis matching Slide 17
    with open(shakespeare_path, 'r', encoding='utf-8') as f:
        full_text = f.read()

    pipe = CustomNLP_Pipeline()
    res = pipe.run_pipeline(full_text)
    bow = res["bow"]
    stem_bow = res["stem_bow"]

    # Top 15 Words
    top_15_words = sorted(bow.items(), key=lambda x: x[1], reverse=True)[:15]
    df_top_words = pd.DataFrame(top_15_words, columns=["Word", "Frequency"])
    df_top_words.to_csv(os.path.join(RESULTS_DIR, "shakespeare_top_words.csv"), index=False)

    fig, ax = plt.subplots(figsize=(10, 6))
    words = [w for w, _ in reversed(top_15_words)]
    counts = [c for _, c in reversed(top_15_words)]
    bars = ax.barh(words, counts, color='#1F4E79', edgecolor='black', height=0.65)
    ax.set_xlabel('Term Frequency', fontsize=12, fontweight='bold')
    ax.set_title("Shakespeare's Complete Works: Top 15 Most Frequent Content Words\n(Stage directions and standard stopwords removed)",
                 fontsize=13, fontweight='bold')
    ax.grid(axis='x', linestyle='--', alpha=0.7)
    for bar in bars:
        w = bar.get_width()
        ax.text(w + 30, bar.get_y() + bar.get_height()/2, f"{int(w):,}", va='center', fontsize=10, fontweight='bold')
    ax.set_xlim(0, max(counts) * 1.15)
    plt.tight_layout()
    out_bow_plot = os.path.join(RESULTS_DIR, "nlp_top_words_bow.png")
    plt.savefig(out_bow_plot, dpi=300)
    plt.close()
    print(f"Saved: {out_bow_plot}")

    # Mood / Thematic Analysis
    mood_data = ShakespeareMoodAnalyzer.analyze_mood(bow)
    mood_rows = []
    for cat, data in mood_data.items():
        top_str = ", ".join([f"{t} ({c})" for t, c in data["top_terms"][:4]])
        mood_rows.append({
            "Theme": cat,
            "Total_Occurrences": data["count"],
            "Corpus_Thematic_Share_Pct": data["percentage"],
            "Representative_Terms": top_str
        })
    df_mood = pd.DataFrame(mood_rows)
    df_mood.to_csv(os.path.join(RESULTS_DIR, "shakespeare_mood_analysis.csv"), index=False)

    # Plot Mood Distribution
    fig, ax = plt.subplots(figsize=(9, 6))
    themes = df_mood['Theme'].values
    shares = df_mood['Corpus_Thematic_Share_Pct'].values
    colors = ['#FFD166', '#EF476F', '#06D6A0', '#118AB2', '#073B4C', '#7209B7']
    bars = ax.bar(themes, shares, color=colors, edgecolor='black', width=0.55)
    ax.set_ylabel('Thematic Category Share (%)', fontsize=12, fontweight='bold')
    ax.set_title("Thematic Sentiment & Mood Distribution in Shakespeare's Works", fontsize=13, fontweight='bold')
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

    print("\nGenerating Graph Benchmarks and Scaling Plots...")
    generate_graph_benchmark_plots_and_csv()

    print("\nGenerating NLP Benchmarks, BoW, and Mood Plots...")
    generate_nlp_benchmark_plots_and_csv()

    print("\nAll figures and results generated successfully!")
