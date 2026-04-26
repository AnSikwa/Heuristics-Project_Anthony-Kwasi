"""
CS 57200 - Heuristic Problem Solving
Phase 3 ablation chart generation.

Reads ablation_4x4_d{20,30,50}.json and produces publication-quality
charts with 95% confidence intervals (bootstrap) into charts_phase3/.

Charts produced:
    chart1_nodes_by_heuristic.png    bar plot, mean nodes per heuristic
                                     across scramble depths (log scale)
    chart2_time_by_heuristic.png     bar plot, mean ms per heuristic
                                     across scramble depths
    chart3_speedup_vs_baseline.png   speedup ratios vs Manhattan baseline
    chart4_nodes_box.png             box plots showing distribution
    chart5_scaling_curve.png         mean nodes vs scramble depth, log
"""

import json
import os
import statistics
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np

CHART_DIR = "charts_phase3"
os.makedirs(CHART_DIR, exist_ok=True)

DEPTH_FILES = {
    20: "ablation_4x4_d20.json",
    30: "ablation_4x4_d30.json",
    50: "ablation_4x4_d50.json",
}
HEURISTICS = ("manhattan", "linear", "pdb")
HEUR_LABELS = {
    "manhattan": "Manhattan",
    "linear": "Linear Conflict",
    "pdb": "Disjoint PDB (4-4-4-3)",
}
HEUR_COLOURS = {
    "manhattan": "#a83232",
    "linear": "#3274a8",
    "pdb": "#2e8a3e",
}


def bootstrap_ci(values: List[float], n_boot: int = 1000,
                 alpha: float = 0.05,
                 rng_seed: int = 0) -> Tuple[float, float, float]:
    """
    Compute the bootstrap mean and a (1 - alpha) CI for ``values``.

    Args:
        values: list of numeric samples.
        n_boot: number of bootstrap resamples.
        alpha: two-sided significance level (0.05 -> 95% CI).
        rng_seed: deterministic seed.

    Returns:
        (mean, ci_low, ci_high)
    """
    if not values:
        return (0.0, 0.0, 0.0)
    rng = np.random.default_rng(rng_seed)
    arr = np.asarray(values, dtype=float)
    boots = np.empty(n_boot)
    for i in range(n_boot):
        sample = rng.choice(arr, size=len(arr), replace=True)
        boots[i] = sample.mean()
    return (
        float(arr.mean()),
        float(np.quantile(boots, alpha / 2)),
        float(np.quantile(boots, 1 - alpha / 2)),
    )


def load_all() -> Dict[int, Dict]:
    """Load every depth's JSON into {depth: data} dict."""
    out = {}
    for d, p in DEPTH_FILES.items():
        if os.path.exists(p):
            out[d] = json.load(open(p))
    return out


def collect_metric(data: Dict, heuristic: str, alg: str,
                   metric: str) -> List[float]:
    """Pull a metric across all solved runs for one heuristic+alg."""
    runs = data["heuristics"][heuristic][alg]
    return [r[metric] for r in runs if r["solved"]]


def chart1_nodes_grouped_bar(all_data: Dict[int, Dict]) -> None:
    """Grouped bar chart: mean nodes by heuristic and depth (log y)."""
    fig, ax = plt.subplots(figsize=(9, 5))
    depths = sorted(all_data.keys())
    x = np.arange(len(depths))
    width = 0.25
    for i, h in enumerate(HEURISTICS):
        means, lows, highs = [], [], []
        for d in depths:
            vals = collect_metric(all_data[d], h, "astar", "nodes")
            m, lo, hi = bootstrap_ci(vals)
            means.append(m)
            lows.append(m - lo)
            highs.append(hi - m)
        ax.bar(x + (i - 1) * width, means, width,
               yerr=[lows, highs], capsize=4,
               label=HEUR_LABELS[h], color=HEUR_COLOURS[h])
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels([f"d={d}" for d in depths])
    ax.set_ylabel("Mean nodes expanded (log scale, 95% CI)")
    ax.set_xlabel("Scramble depth")
    ax.set_title("A* nodes expanded by heuristic and scramble depth (4x4)")
    ax.legend()
    ax.grid(True, axis="y", which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(CHART_DIR, "chart1_nodes_by_heuristic.png"),
                dpi=150)
    plt.close(fig)


def chart2_time_grouped_bar(all_data: Dict[int, Dict]) -> None:
    """Grouped bar chart: mean time (ms) by heuristic and depth (log y)."""
    fig, ax = plt.subplots(figsize=(9, 5))
    depths = sorted(all_data.keys())
    x = np.arange(len(depths))
    width = 0.25
    for i, h in enumerate(HEURISTICS):
        means, lows, highs = [], [], []
        for d in depths:
            vals = collect_metric(all_data[d], h, "astar", "time_ms")
            m, lo, hi = bootstrap_ci(vals)
            means.append(m)
            lows.append(m - lo)
            highs.append(hi - m)
        ax.bar(x + (i - 1) * width, means, width,
               yerr=[lows, highs], capsize=4,
               label=HEUR_LABELS[h], color=HEUR_COLOURS[h])
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels([f"d={d}" for d in depths])
    ax.set_ylabel("Mean wall-clock time per instance (ms, log, 95% CI)")
    ax.set_xlabel("Scramble depth")
    ax.set_title("A* wall-clock time by heuristic and scramble depth (4x4)")
    ax.legend()
    ax.grid(True, axis="y", which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(CHART_DIR, "chart2_time_by_heuristic.png"),
                dpi=150)
    plt.close(fig)


def chart3_speedup(all_data: Dict[int, Dict]) -> None:
    """Speedup over Manhattan baseline at each scramble depth."""
    fig, ax = plt.subplots(figsize=(8, 5))
    depths = sorted(all_data.keys())
    for h in ("linear", "pdb"):
        ratios = []
        for d in depths:
            base = collect_metric(all_data[d], "manhattan", "astar", "nodes")
            this = collect_metric(all_data[d], h, "astar", "nodes")
            if base and this:
                ratios.append(statistics.mean(base) / statistics.mean(this))
        ax.plot(depths, ratios, marker="o", linewidth=2,
                label=HEUR_LABELS[h], color=HEUR_COLOURS[h])
        for x, y in zip(depths, ratios):
            ax.annotate(f"{y:.1f}x", (x, y),
                        textcoords="offset points", xytext=(0, 8),
                        ha="center", fontsize=9)
    ax.axhline(y=1.0, linestyle="--", color="gray", alpha=0.5,
               label="Manhattan baseline")
    ax.set_xlabel("Scramble depth")
    ax.set_ylabel("Node-expansion speedup vs Manhattan baseline")
    ax.set_title("Heuristic speedup over Manhattan baseline (A*, 4x4)")
    ax.set_xticks(depths)
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(CHART_DIR, "chart3_speedup_vs_baseline.png"),
                dpi=150)
    plt.close(fig)


def chart4_nodes_box(all_data: Dict[int, Dict]) -> None:
    """Box plots of node distributions for the hardest depth."""
    deepest = max(all_data.keys())
    fig, ax = plt.subplots(figsize=(8, 5))
    boxes = []
    labels = []
    colours = []
    for h in HEURISTICS:
        vals = collect_metric(all_data[deepest], h, "astar", "nodes")
        boxes.append(vals)
        labels.append(HEUR_LABELS[h])
        colours.append(HEUR_COLOURS[h])
    bp = ax.boxplot(boxes, labels=labels, patch_artist=True, showmeans=True)
    for patch, c in zip(bp["boxes"], colours):
        patch.set_facecolor(c)
        patch.set_alpha(0.6)
    ax.set_yscale("log")
    ax.set_ylabel("Nodes expanded (log scale)")
    ax.set_title(f"A* node-expansion distribution at scramble depth "
                 f"{deepest} (4x4)")
    ax.grid(True, axis="y", which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(CHART_DIR, "chart4_nodes_box.png"), dpi=150)
    plt.close(fig)


def chart5_scaling_curve(all_data: Dict[int, Dict]) -> None:
    """Scaling curves: mean nodes vs scramble depth on log scale."""
    fig, ax = plt.subplots(figsize=(8, 5))
    depths = sorted(all_data.keys())
    for h in HEURISTICS:
        means, lows, highs = [], [], []
        for d in depths:
            vals = collect_metric(all_data[d], h, "astar", "nodes")
            m, lo, hi = bootstrap_ci(vals)
            means.append(m)
            lows.append(lo)
            highs.append(hi)
        means_arr = np.array(means)
        lows_arr = np.array(lows)
        highs_arr = np.array(highs)
        ax.plot(depths, means_arr, marker="o", linewidth=2,
                label=HEUR_LABELS[h], color=HEUR_COLOURS[h])
        ax.fill_between(depths, lows_arr, highs_arr, alpha=0.2,
                        color=HEUR_COLOURS[h])
    ax.set_yscale("log")
    ax.set_xlabel("Scramble depth")
    ax.set_ylabel("Mean nodes expanded (log scale)")
    ax.set_title("Scaling: mean A* nodes vs scramble depth (4x4)")
    ax.set_xticks(depths)
    ax.legend()
    ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(CHART_DIR, "chart5_scaling_curve.png"),
                dpi=150)
    plt.close(fig)


def chart6_architecture() -> None:
    """
    Static architecture-style diagram drawn with matplotlib so the
    final report has a system diagram (rubric A3 requires one).
    """
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 6)
    ax.axis("off")

    def box(x, y, w, h, text, color="#dceffd", edge="#1f3b6b"):
        rect = plt.Rectangle((x, y), w, h, facecolor=color,
                             edgecolor=edge, linewidth=1.5)
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h / 2, text,
                ha="center", va="center", fontsize=10, wrap=True)

    def arrow(x1, y1, x2, y2):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", lw=1.5,
                                    color="#1f3b6b"))

    # Layer 1: instance generation
    box(0.3, 5.0, 2.4, 0.7,
        "Solvable instance\n(random walk from goal)",
        color="#fdebd0")
    # Layer 2: state representation
    box(0.3, 4.0, 2.4, 0.7,
        "Tuple state\n(immutable, hashable)",
        color="#fdebd0")
    arrow(1.5, 5.0, 1.5, 4.7)
    # Heuristics
    box(3.5, 5.0, 2.4, 0.7, "Manhattan distance", color="#f8d7da")
    box(3.5, 4.0, 2.4, 0.7,
        "Linear Conflict\n(Hansson 1992)", color="#f8d7da")
    box(3.5, 3.0, 2.4, 0.7,
        "Disjoint PDB\n(Korf & Felner 2002)", color="#f8d7da")
    # Algorithms
    box(6.7, 5.0, 2.0, 0.7, "BFS (uninformed)", color="#d4edda")
    box(6.7, 4.0, 2.0, 0.7, "A* (best-first)", color="#d4edda")
    box(6.7, 3.0, 2.0, 0.7, "IDA* (low-memory)", color="#d4edda")
    # Output
    box(9.1, 4.0, 1.7, 0.7, "Result dict\n(nodes/depth/time)",
        color="#cce5ff")

    # Connections
    arrow(2.7, 4.35, 3.5, 4.35)
    arrow(5.9, 5.35, 6.7, 5.35)
    arrow(5.9, 4.35, 6.7, 4.35)
    arrow(5.9, 3.35, 6.7, 3.35)
    arrow(8.7, 4.35, 9.1, 4.35)

    # Outer frames
    ax.text(1.5, 5.85, "INSTANCE LAYER", ha="center",
            fontsize=10, fontweight="bold", color="#1f3b6b")
    ax.text(4.7, 5.85, "HEURISTICS", ha="center",
            fontsize=10, fontweight="bold", color="#1f3b6b")
    ax.text(7.7, 5.85, "SEARCH ALGORITHMS", ha="center",
            fontsize=10, fontweight="bold", color="#1f3b6b")
    ax.text(9.95, 5.85, "OUTPUT", ha="center",
            fontsize=10, fontweight="bold", color="#1f3b6b")

    # Experiment harness footer
    box(0.3, 1.5, 10.5, 1.0,
        "Experiment harness: ablation.py\n"
        "Seed = 1234; 50 instances per scramble depth (20, 30); "
        "30 instances at depth 50; results -> JSON",
        color="#eeeeee")
    arrow(5.5, 3.0, 5.5, 2.5)

    box(0.3, 0.2, 10.5, 1.0,
        "Visualisation & reporting: ablation_charts.py, "
        "make_report.py, make_*_report.py (matplotlib + ReportLab)",
        color="#eeeeee")
    arrow(5.5, 1.5, 5.5, 1.2)

    fig.suptitle("System Architecture - Phase 3 (heuristic ablation)",
                 fontsize=12, fontweight="bold")
    fig.savefig(os.path.join(CHART_DIR, "chart6_architecture.png"),
                dpi=160, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    """Generate all Phase 3 charts."""
    all_data = load_all()
    if not all_data:
        raise SystemExit("No ablation_*.json files found. Run ablation.py first.")
    chart1_nodes_grouped_bar(all_data)
    chart2_time_grouped_bar(all_data)
    chart3_speedup(all_data)
    chart4_nodes_box(all_data)
    chart5_scaling_curve(all_data)
    chart6_architecture()
    print(f"Charts written to {CHART_DIR}/")


if __name__ == "__main__":
    main()
