"""
Depth-scaling charts for CS 57200.
Shows how A*/IDA*/BFS node expansions scale with scramble depth and actual solution depth.
"""

import json, numpy as np
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

ROOT       = Path(__file__).parent
DATA_DIR   = ROOT / "data"
CHARTS_DIR = ROOT / "charts"
CHARTS_DIR.mkdir(exist_ok=True)

# ── Palette ──────────────────────────────────────────────
TEAL  = "#20808D"; RUST  = "#A84B2F"; DARK  = "#1B474D"
GOLD  = "#E8AF34"; BG    = "#F7F6F2"; TEXT  = "#28251D"
MUT   = "#7A7974"; BORD  = "#D4D1CA"

plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": BG, "axes.edgecolor": BORD,
    "axes.labelcolor": TEXT, "text.color": TEXT, "xtick.color": MUT, "ytick.color": MUT,
    "grid.color": BORD, "grid.linestyle": "--", "grid.linewidth": 0.5,
    "font.family": "DejaVu Sans", "font.size": 10, "axes.titlesize": 12,
    "axes.titleweight": "bold", "axes.labelsize": 10,
    "legend.framealpha": 0.92, "legend.edgecolor": BORD, "figure.dpi": 150,
})

FW, FH = 6.857, 4.0   # ratio matches 6:3.5 PDF embed

with open(DATA_DIR / "depth_scaling_results.json") as f:
    raw = json.load(f)

DEPTHS = [10, 20, 30, 50, 75]

def mean_nodes(sd_key, algo):
    recs = raw[sd_key][algo]
    ns = [r["nodes"] for r in recs if r["found"]]
    return sum(ns)/len(ns) if ns else 0

def mean_depth(sd_key, algo):
    recs = raw[sd_key][algo]
    ds = [r["depth"] for r in recs if r["found"] and r["depth"] >= 0]
    return sum(ds)/len(ds) if ds else 0

def mean_time(sd_key, algo):
    recs = raw[sd_key][algo]
    ts = [r["ms"] for r in recs if r["found"]]
    return sum(ts)/len(ts) if ts else 0

# ─────────────────────────────────────────────────────────
# Chart A: Mean nodes expanded vs scramble depth (log scale)
# ─────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(FW, FH))

bfs_n  = [mean_nodes(str(d), "bfs")     for d in DEPTHS]
ast_n  = [mean_nodes(str(d), "astar")   for d in DEPTHS]
ida_n  = [mean_nodes(str(d), "idastar") for d in DEPTHS]

ax.plot(DEPTHS, bfs_n,  "o-", color=RUST, linewidth=2.2, markersize=6, label="BFS (baseline)")
ax.plot(DEPTHS, ast_n,  "s-", color=TEAL, linewidth=2.2, markersize=6, label="A* (Manhattan)")
ax.plot(DEPTHS, ida_n,  "^-", color=DARK, linewidth=2.2, markersize=6, label="IDA* (Manhattan)")

# value labels on A* and BFS
for x, y in zip(DEPTHS, bfs_n):
    ax.annotate(f"{y:,.0f}", (x, y), textcoords="offset points", xytext=(0, 8),
                ha="center", fontsize=7.5, color=RUST)
for x, y in zip(DEPTHS, ast_n):
    ax.annotate(f"{y:,.0f}", (x, y), textcoords="offset points", xytext=(0, -14),
                ha="center", fontsize=7.5, color=TEAL)

ax.set_yscale("log")
ax.set_xlabel("Scramble Depth (random moves from goal)")
ax.set_ylabel("Mean Nodes Expanded (log scale)")
ax.set_title("Node Expansions vs. Scramble Depth — 3×3 Puzzle (50 instances each)")
ax.set_xticks(DEPTHS)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
ax.legend(loc="upper left"); ax.grid(True, which="both"); ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig(CHARTS_DIR / "chartA_nodes_vs_scramble_log.png",
            bbox_inches="tight", pad_inches=0.05)
plt.close(); print("Chart A saved.")

# ─────────────────────────────────────────────────────────
# Chart B: Mean nodes vs actual solution depth (scatter + line)
# ─────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(FW, FH))

# Per-instance scatter (A* only, all scramble depths, colour-coded by scramble depth)
cmap = plt.cm.get_cmap("YlOrBr", len(DEPTHS))
depth_colors = {str(d): cmap(i) for i, d in enumerate(DEPTHS)}

for i, sd in enumerate(DEPTHS):
    recs = raw[str(sd)]["astar"]
    xs = [r["depth"] for r in recs if r["found"] and r["depth"] >= 0]
    ys = [r["nodes"] for r in recs if r["found"] and r["depth"] >= 0]
    ax.scatter(xs, ys, color=depth_colors[str(sd)], alpha=0.65, s=28,
               label=f"Scramble {sd}" if i < 5 else None, zorder=3)

# Mean line connecting scramble-depth groups
mx = [mean_depth(str(d), "astar") for d in DEPTHS]
my = [mean_nodes(str(d), "astar") for d in DEPTHS]
ax.plot(mx, my, "s--", color=TEAL, linewidth=1.8, markersize=7,
        label="A* mean per scramble depth", zorder=5)

# BFS mean line for comparison
bx = [mean_depth(str(d), "bfs") for d in DEPTHS]
by = [mean_nodes(str(d), "bfs") for d in DEPTHS]
ax.plot(bx, by, "o--", color=RUST, linewidth=1.8, markersize=7,
        label="BFS mean per scramble depth", zorder=5)

ax.set_yscale("log")
ax.set_xlabel("Optimal Solution Depth (moves)")
ax.set_ylabel("Nodes Expanded (log scale)")
ax.set_title("A* Nodes Expanded vs. Actual Solution Depth — 3×3 Puzzle")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
ax.legend(fontsize=8, loc="upper left"); ax.grid(True, which="both"); ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig(CHARTS_DIR / "chartB_nodes_vs_actual_depth.png",
            bbox_inches="tight", pad_inches=0.05)
plt.close(); print("Chart B saved.")

# ─────────────────────────────────────────────────────────
# Chart C: BFS/A*/IDA* speedup ratio vs scramble depth
# ─────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(FW, FH))

ratios_ba  = [mean_nodes(str(d), "bfs") / mean_nodes(str(d), "astar")   for d in DEPTHS]
ratios_bi  = [mean_nodes(str(d), "bfs") / mean_nodes(str(d), "idastar") for d in DEPTHS]
ratios_ai  = [mean_nodes(str(d), "astar") / mean_nodes(str(d), "idastar") for d in DEPTHS]

ax.plot(DEPTHS, ratios_ba, "o-", color=RUST, linewidth=2.2, markersize=7, label="BFS / A*  (heuristic gain)")
ax.plot(DEPTHS, ratios_bi, "s-", color=DARK, linewidth=2.2, markersize=7, label="BFS / IDA*")
ax.plot(DEPTHS, ratios_ai, "^-", color=GOLD, linewidth=2.0, markersize=6, label="A* / IDA*  (≈1 = comparable)")

for x, y in zip(DEPTHS, ratios_ba):
    ax.annotate(f"{y:.0f}×", (x, y), textcoords="offset points", xytext=(0, 7),
                ha="center", fontsize=7.5, color=RUST)

ax.axhline(1, color=MUT, linewidth=1, linestyle=":")
ax.set_xlabel("Scramble Depth")
ax.set_ylabel("Node Expansion Ratio  (higher = bigger A* advantage)")
ax.set_title("Heuristic Gain: BFS÷A* Node Expansion Ratio vs. Scramble Depth")
ax.set_xticks(DEPTHS)
ax.legend(fontsize=9); ax.yaxis.grid(True); ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig(CHARTS_DIR / "chartC_ratio_vs_scramble.png",
            bbox_inches="tight", pad_inches=0.05)
plt.close(); print("Chart C saved.")

# ─────────────────────────────────────────────────────────
# Chart D: Runtime (ms) vs scramble depth
# ─────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(FW, FH))

bfs_t = [mean_time(str(d), "bfs")     for d in DEPTHS]
ast_t = [mean_time(str(d), "astar")   for d in DEPTHS]
ida_t = [mean_time(str(d), "idastar") for d in DEPTHS]

ax.plot(DEPTHS, bfs_t, "o-", color=RUST, linewidth=2.2, markersize=6, label="BFS")
ax.plot(DEPTHS, ast_t, "s-", color=TEAL, linewidth=2.2, markersize=6, label="A* (Manhattan)")
ax.plot(DEPTHS, ida_t, "^-", color=DARK, linewidth=2.2, markersize=6, label="IDA* (Manhattan)")

ax.fill_between(DEPTHS, ast_t, ida_t, alpha=0.10, color=TEAL)

for x, y in zip(DEPTHS, bfs_t):
    ax.annotate(f"{y:.0f} ms", (x, y), textcoords="offset points", xytext=(0, 8),
                ha="center", fontsize=7.5, color=RUST)

ax.set_xlabel("Scramble Depth")
ax.set_ylabel("Mean Runtime (ms)")
ax.set_title("Mean Runtime vs. Scramble Depth — 3×3 Puzzle")
ax.set_xticks(DEPTHS)
ax.legend(); ax.yaxis.grid(True); ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig(CHARTS_DIR / "chartD_runtime_vs_scramble.png",
            bbox_inches="tight", pad_inches=0.05)
plt.close(); print("Chart D saved.")

# ─────────────────────────────────────────────────────────
# Chart E: Actual solution depth distribution per scramble level (violin)
# ─────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(FW, FH))

depth_data = [
    [r["depth"] for r in raw[str(d)]["astar"] if r["found"] and r["depth"] >= 0]
    for d in DEPTHS
]

positions = list(range(1, len(DEPTHS)+1))
parts = ax.violinplot(depth_data, positions=positions, showmedians=True, widths=0.55)
for pc in parts["bodies"]:
    pc.set_facecolor(TEAL); pc.set_alpha(0.72)
parts["cmedians"].set_color("white"); parts["cmedians"].set_linewidth(2)
for key in ["cbars","cmins","cmaxes"]: parts[key].set_color(MUT)

# scatter individual points
for i, (dd, pos) in enumerate(zip(depth_data, positions)):
    jitter = np.random.default_rng(i).uniform(-0.08, 0.08, len(dd))
    ax.scatter(np.array([pos]*len(dd)) + jitter, dd, color=TEAL, alpha=0.35, s=12, zorder=3)

ax.set_xticks(positions)
ax.set_xticklabels([f"Scramble\n{d}" for d in DEPTHS])
ax.set_ylabel("Optimal Solution Depth (moves)")
ax.set_title("Solution Depth Distribution by Scramble Level — 3×3 Puzzle")
ax.yaxis.grid(True); ax.set_axisbelow(True)

# annotate medians
for pos, dd in zip(positions, depth_data):
    med = float(np.median(dd))
    ax.text(pos, med + 0.3, f"med={med:.0f}", ha="center", fontsize=7.5,
            color=TEXT, weight="bold")

plt.tight_layout()
plt.savefig(CHARTS_DIR / "chartE_depth_distribution.png",
            bbox_inches="tight", pad_inches=0.05)
plt.close(); print("Chart E saved.")

# ── Print summary table ───────────────────────────────────
print("\n" + "="*85)
print(f"{'Scramble':>8}  {'Sol.Depth':>9}  {'BFS nodes':>10}  {'A* nodes':>9}  {'IDA* nodes':>10}  {'BFS/A*':>6}")
print("="*85)
for d in DEPTHS:
    sd = mean_depth(str(d), "astar")
    bn = mean_nodes(str(d), "bfs")
    an = mean_nodes(str(d), "astar")
    in_ = mean_nodes(str(d), "idastar")
    ratio = bn/an if an else 0
    print(f"{d:>8}  {sd:>9.1f}  {bn:>10,.0f}  {an:>9,.0f}  {in_:>10,.0f}  {ratio:>5.0f}×")
print("="*85)
