"""Generate publication-quality charts for CS 57200 Phase 2 report."""

import json
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

os.makedirs("/home/user/workspace/cs57200/charts", exist_ok=True)

# ─── palette (design-foundations Nexus) ───
TEAL  = "#20808D"
RUST  = "#A84B2F"
DARK  = "#1B474D"
GOLD  = "#FFC553"
BG    = "#F7F6F2"
TEXT  = "#28251D"
MUT   = "#7A7974"
BORD  = "#D4D1CA"

plt.rcParams.update({
    "figure.facecolor": BG,
    "axes.facecolor":   BG,
    "axes.edgecolor":   BORD,
    "axes.labelcolor":  TEXT,
    "text.color":       TEXT,
    "xtick.color":      MUT,
    "ytick.color":      MUT,
    "grid.color":       BORD,
    "grid.linestyle":   "--",
    "grid.linewidth":   0.5,
    "font.family":      "DejaVu Sans",
    "font.size":        10,
    "axes.titlesize":   12,
    "axes.titleweight": "bold",
    "axes.labelsize":   10,
    "legend.framealpha": 0.9,
    "legend.edgecolor": BORD,
    "figure.dpi":       150,
})

def safe_vals(lst):
    return [v for v in lst if v is not None and v >= 0]

with open("/home/user/workspace/cs57200/raw_results.json") as f:
    raw = json.load(f)

# ═══════════════════════════════════════════════════════
# Chart 1: Nodes Expanded – Box plot, 3x3 BFS vs A* vs IDA*
# ═══════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(7, 4.5))
fig.patch.set_facecolor(BG)

bfs_nodes  = safe_vals(raw["3x3"]["bfs"]["nodes"])
ast_nodes  = safe_vals(raw["3x3"]["astar"]["nodes"])
ida_nodes  = safe_vals(raw["3x3"]["idastar"]["nodes"])

data  = [bfs_nodes, ast_nodes, ida_nodes]
labels = ["BFS", "A*\n(Manhattan)", "IDA*\n(Manhattan)"]
colors = [RUST, TEAL, DARK]

bp = ax.boxplot(data, patch_artist=True, widths=0.5,
                medianprops=dict(color="white", linewidth=2),
                whiskerprops=dict(color=MUT),
                capprops=dict(color=MUT),
                flierprops=dict(marker="o", color=RUST, alpha=0.4, markersize=4))

for patch, c in zip(bp["boxes"], colors):
    patch.set_facecolor(c)
    patch.set_alpha(0.85)

ax.set_xticks([1, 2, 3])
ax.set_xticklabels(labels)
ax.set_ylabel("Nodes Expanded")
ax.set_title("Nodes Expanded — 3×3 Puzzle (100 instances)")
ax.yaxis.grid(True)
ax.set_axisbelow(True)

# annotation
ax.annotate(f"BFS median: {int(np.median(bfs_nodes)):,}",
            xy=(1, np.median(bfs_nodes)), xytext=(1.4, np.median(bfs_nodes)*1.15),
            fontsize=8, color=RUST,
            arrowprops=dict(arrowstyle="->", color=RUST, lw=0.8))
ax.annotate(f"A* median: {int(np.median(ast_nodes)):,}",
            xy=(2, np.median(ast_nodes)), xytext=(2.3, np.median(ast_nodes)*3),
            fontsize=8, color=TEAL,
            arrowprops=dict(arrowstyle="->", color=TEAL, lw=0.8))

plt.tight_layout()
plt.savefig("/home/user/workspace/cs57200/charts/chart1_nodes_boxplot_3x3.png", bbox_inches="tight")
plt.close()
print("Chart 1 saved.")

# ═══════════════════════════════════════════════════════
# Chart 2: Mean Nodes Expanded — grouped bar 3x3 vs 4x4
# ═══════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(7, 4.5))

algos = ["A*\n(Manhattan)", "IDA*\n(Manhattan)"]
keys  = ["astar", "idastar"]
x = np.arange(len(algos))
w = 0.32

vals_3 = [np.mean(safe_vals(raw["3x3"][k]["nodes"])) for k in keys]
vals_4 = [np.mean(safe_vals(raw["4x4"][k]["nodes"])) for k in keys]

b1 = ax.bar(x - w/2, vals_3, w, label="3×3 (8-puzzle)",  color=TEAL, alpha=0.88)
b2 = ax.bar(x + w/2, vals_4, w, label="4×4 (15-puzzle)", color=RUST, alpha=0.88)

for bar in list(b1) + list(b2):
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, h + max(vals_3 + vals_4)*0.01,
            f"{h:,.0f}", ha="center", va="bottom", fontsize=8, color=TEXT)

ax.set_xticks(x)
ax.set_xticklabels(algos)
ax.set_ylabel("Mean Nodes Expanded")
ax.set_title("Mean Nodes Expanded: A* vs IDA* (3×3 and 4×4)")
ax.legend()
ax.yaxis.grid(True)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig("/home/user/workspace/cs57200/charts/chart2_nodes_grouped_bar.png", bbox_inches="tight")
plt.close()
print("Chart 2 saved.")

# ═══════════════════════════════════════════════════════
# Chart 3: Runtime distribution — violin plot 3x3
# ═══════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(7, 4.5))

bfs_t  = safe_vals(raw["3x3"]["bfs"]["time_ms"])
ast_t  = safe_vals(raw["3x3"]["astar"]["time_ms"])
ida_t  = safe_vals(raw["3x3"]["idastar"]["time_ms"])

vdata  = [bfs_t, ast_t, ida_t]
parts = ax.violinplot(vdata, positions=[1, 2, 3], showmedians=True, widths=0.6)

vc = [RUST, TEAL, DARK]
for i, (pc, c) in enumerate(zip(parts["bodies"], vc)):
    pc.set_facecolor(c)
    pc.set_alpha(0.75)
parts["cmedians"].set_color("white")
parts["cmedians"].set_linewidth(2)
for key in ["cbars", "cmins", "cmaxes"]:
    parts[key].set_color(MUT)

ax.set_xticks([1, 2, 3])
ax.set_xticklabels(["BFS", "A* (Manhattan)", "IDA* (Manhattan)"])
ax.set_ylabel("Runtime (ms)")
ax.set_title("Runtime Distribution — 3×3 Puzzle (100 instances)")
ax.yaxis.grid(True)
ax.set_axisbelow(True)

# means
for pos, vals in zip([1, 2, 3], vdata):
    m = np.mean(vals)
    ax.scatter(pos, m, color="white", s=40, zorder=5, edgecolors=TEXT, linewidths=0.8)

legend_handles = [
    mpatches.Patch(facecolor=RUST,  label=f"BFS  (mean={np.mean(bfs_t):.1f} ms)"),
    mpatches.Patch(facecolor=TEAL,  label=f"A*   (mean={np.mean(ast_t):.1f} ms)"),
    mpatches.Patch(facecolor=DARK,  label=f"IDA* (mean={np.mean(ida_t):.1f} ms)"),
]
ax.legend(handles=legend_handles, fontsize=8)

plt.tight_layout()
plt.savefig("/home/user/workspace/cs57200/charts/chart3_runtime_violin_3x3.png", bbox_inches="tight")
plt.close()
print("Chart 3 saved.")

# ═══════════════════════════════════════════════════════
# Chart 4: Solution Depth vs Nodes Expanded (scatter) — A* 3x3
# ═══════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(7, 4.5))

depths_a = [d for d, n in zip(raw["3x3"]["astar"]["depth"], raw["3x3"]["astar"]["nodes"])
            if d is not None and n is not None]
nodes_a  = [n for d, n in zip(raw["3x3"]["astar"]["depth"], raw["3x3"]["astar"]["nodes"])
            if d is not None and n is not None]

depths_b = [d for d, n in zip(raw["3x3"]["bfs"]["depth"], raw["3x3"]["bfs"]["nodes"])
            if d is not None and n is not None]
nodes_b  = [n for d, n in zip(raw["3x3"]["bfs"]["depth"], raw["3x3"]["bfs"]["nodes"])
            if d is not None and n is not None]

ax.scatter(depths_b, nodes_b, color=RUST, alpha=0.5, s=22, label="BFS")
ax.scatter(depths_a, nodes_a, color=TEAL, alpha=0.6, s=22, label="A* (Manhattan)")

# trend lines
if len(depths_b) > 1:
    z = np.polyfit(depths_b, nodes_b, 2)
    p = np.poly1d(z)
    xs = np.linspace(min(depths_b), max(depths_b), 100)
    ax.plot(xs, p(xs), color=RUST, linewidth=1.5, linestyle="--", alpha=0.8)
if len(depths_a) > 1:
    z = np.polyfit(depths_a, nodes_a, 2)
    p = np.poly1d(z)
    xs = np.linspace(min(depths_a), max(depths_a), 100)
    ax.plot(xs, p(xs), color=TEAL, linewidth=1.5, linestyle="--", alpha=0.8)

ax.set_xlabel("Optimal Solution Depth (moves)")
ax.set_ylabel("Nodes Expanded")
ax.set_title("Solution Depth vs. Nodes Expanded — 3×3 Puzzle")
ax.legend()
ax.yaxis.grid(True)
ax.xaxis.grid(True)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig("/home/user/workspace/cs57200/charts/chart4_depth_vs_nodes_scatter.png", bbox_inches="tight")
plt.close()
print("Chart 4 saved.")

# ═══════════════════════════════════════════════════════
# Chart 5: Mean Runtime A* vs IDA* — 3x3 and 4x4 side by side
# ═══════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(7, 4.5))

sizes = ["3×3", "4×4"]
astar_times  = [np.mean(safe_vals(raw["3x3"]["astar"]["time_ms"])),
                np.mean(safe_vals(raw["4x4"]["astar"]["time_ms"]))]
idastar_times= [np.mean(safe_vals(raw["3x3"]["idastar"]["time_ms"])),
                np.mean(safe_vals(raw["4x4"]["idastar"]["time_ms"]))]

x = np.arange(len(sizes))
b1 = ax.bar(x - w/2, astar_times,  w, label="A* (Manhattan)",  color=TEAL, alpha=0.88)
b2 = ax.bar(x + w/2, idastar_times, w, label="IDA* (Manhattan)", color=DARK, alpha=0.88)

for bar in list(b1) + list(b2):
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, h + 0.05,
            f"{h:.2f} ms", ha="center", va="bottom", fontsize=8, color=TEXT)

ax.set_xticks(x)
ax.set_xticklabels(sizes)
ax.set_ylabel("Mean Runtime (ms)")
ax.set_title("Mean Runtime: A* vs IDA* by Puzzle Size")
ax.legend()
ax.yaxis.grid(True)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig("/home/user/workspace/cs57200/charts/chart5_runtime_bar_by_size.png", bbox_inches="tight")
plt.close()
print("Chart 5 saved.")

print("\nAll charts generated in /home/user/workspace/cs57200/charts/")
