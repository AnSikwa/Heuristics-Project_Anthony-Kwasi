"""Charts for the 4x4 depth-scaling experiment."""

import json, numpy as np, math, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches

os.makedirs("/home/user/workspace/cs57200/charts4x4", exist_ok=True)

TEAL  = "#20808D"; RUST  = "#A84B2F"; DARK  = "#1B474D"
GOLD  = "#E8AF34"; BG    = "#F7F6F2"; TEXT  = "#28251D"
MUT   = "#7A7974"; BORD  = "#D4D1CA"; MAUVE = "#944454"

plt.rcParams.update({
    "figure.facecolor": BG,  "axes.facecolor":  BG,  "axes.edgecolor": BORD,
    "axes.labelcolor":  TEXT,"text.color":      TEXT,"xtick.color":    MUT,
    "ytick.color":      MUT, "grid.color":      BORD,"grid.linestyle": "--",
    "grid.linewidth":   0.5, "font.family":     "DejaVu Sans","font.size": 10,
    "axes.titlesize":   12,  "axes.titleweight":"bold","axes.labelsize": 10,
    "legend.framealpha":0.92,"legend.edgecolor":BORD,"figure.dpi":     150,
})
FW, FH = 6.857, 4.0   # ratio ≈ 1.714 to match 6×3.5in PDF embed

with open("/home/user/workspace/cs57200/depth_scaling_4x4_results.json") as f:
    raw = json.load(f)

DEPTHS = sorted(raw.keys(), key=int)
DEPTHS_INT = [int(d) for d in DEPTHS]

def mean_n(sd, algo):
    ns=[r["nodes"] for r in raw[str(sd)][algo] if r["found"]]; return sum(ns)/len(ns) if ns else 0
def mean_d(sd, algo):
    ds=[r["depth"] for r in raw[str(sd)][algo] if r["found"] and r["depth"]>=0]; return sum(ds)/len(ds) if ds else 0
def mean_t(sd, algo):
    ts=[r["ms"] for r in raw[str(sd)][algo] if r["found"]]; return sum(ts)/len(ts) if ts else 0
def solve_rate(sd, algo):
    return sum(1 for r in raw[str(sd)][algo] if r["found"]) / len(raw[str(sd)][algo]) * 100

# ═══════════════════════════════════════════════════════
# Chart 1: Nodes expanded — A* vs IDA* (log scale)
# ═══════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(FW, FH))

an = [mean_n(sd,"astar")   for sd in DEPTHS_INT]
in_= [mean_n(sd,"idastar") for sd in DEPTHS_INT]

ax.plot(DEPTHS_INT, an,  "s-", color=TEAL, lw=2.2, ms=7, label="A* (Manhattan)")
ax.plot(DEPTHS_INT, in_, "^-", color=DARK, lw=2.2, ms=7, label="IDA* (Manhattan)")

# Crossover annotation
ax.axvspan(20, 30, alpha=0.08, color=RUST, label="Crossover zone")
ax.text(25, max(in_)*0.55, "← IDA* ahead\n A* ahead →", ha="center",
        fontsize=8, color=RUST, style="italic")

for x, y in zip(DEPTHS_INT, an):
    ax.annotate(f"{y:,.0f}", (x, y), xytext=(0, 8),
                textcoords="offset points", ha="center", fontsize=7.5, color=TEAL)
for x, y in zip(DEPTHS_INT, in_):
    ax.annotate(f"{y:,.0f}", (x, y), xytext=(0, -15),
                textcoords="offset points", ha="center", fontsize=7.5, color=DARK)

ax.set_yscale("log")
ax.set_xlabel("Scramble Depth (random moves from goal)")
ax.set_ylabel("Mean Nodes Expanded (log scale)")
ax.set_title("Nodes Expanded vs. Scramble Depth — 4×4 Puzzle (50 instances each)")
ax.set_xticks(DEPTHS_INT)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
ax.legend(loc="upper left"); ax.grid(True, which="both"); ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig("/home/user/workspace/cs57200/charts4x4/chart1_nodes_log.png",
            bbox_inches="tight", pad_inches=0.05)
plt.close(); print("Chart 1 saved.")

# ═══════════════════════════════════════════════════════
# Chart 2: A* / IDA* node ratio — who wins by how much
# ═══════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(FW, FH))

ratio = [mean_n(sd,"astar") / mean_n(sd,"idastar") if mean_n(sd,"idastar") else 1
         for sd in DEPTHS_INT]

bar_colors = [TEAL if r <= 1 else RUST for r in ratio]
bars = ax.bar(DEPTHS_INT, ratio, width=7, color=bar_colors, alpha=0.85)
ax.axhline(1.0, color=MUT, lw=1.2, linestyle="--", label="Equal (ratio = 1)")

for bar, r in zip(bars, ratio):
    lbl = f"{r:.2f}×" if r >= 1 else f"1/{1/r:.2f}×"
    ax.text(bar.get_x()+bar.get_width()/2, r + 0.01,
            lbl, ha="center", va="bottom", fontsize=8.5,
            color=TEXT, weight="bold")

ax.set_xlabel("Scramble Depth")
ax.set_ylabel("A* nodes ÷ IDA* nodes  (>1 = IDA* fewer nodes)")
ax.set_title("A* / IDA* Node Expansion Ratio — 4×4 Puzzle\n(bars below 1 = A* expands fewer)")
ax.set_xticks(DEPTHS_INT)
handles = [mpatches.Patch(color=TEAL, label="A* uses fewer nodes"),
           mpatches.Patch(color=RUST, label="IDA* uses fewer nodes")]
ax.legend(handles=handles, fontsize=8.5)
ax.yaxis.grid(True); ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig("/home/user/workspace/cs57200/charts4x4/chart2_ratio.png",
            bbox_inches="tight", pad_inches=0.05)
plt.close(); print("Chart 2 saved.")

# ═══════════════════════════════════════════════════════
# Chart 3: Runtime (ms) — A* vs IDA*
# ═══════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(FW, FH))

at = [mean_t(sd,"astar")   for sd in DEPTHS_INT]
it = [mean_t(sd,"idastar") for sd in DEPTHS_INT]

ax.plot(DEPTHS_INT, at, "s-", color=TEAL, lw=2.2, ms=7, label="A* (Manhattan)")
ax.plot(DEPTHS_INT, it, "^-", color=DARK, lw=2.2, ms=7, label="IDA* (Manhattan)")
ax.fill_between(DEPTHS_INT, at, it, alpha=0.10, color=TEAL)

for x, y in zip(DEPTHS_INT, at):
    ax.annotate(f"{y:.0f} ms", (x, y), xytext=(0, 8),
                textcoords="offset points", ha="center", fontsize=7.5, color=TEAL)
for x, y in zip(DEPTHS_INT, it):
    ax.annotate(f"{y:.0f} ms", (x, y), xytext=(0, -15),
                textcoords="offset points", ha="center", fontsize=7.5, color=DARK)

ax.set_xlabel("Scramble Depth")
ax.set_ylabel("Mean Runtime (ms)")
ax.set_title("Mean Runtime vs. Scramble Depth — 4×4 Puzzle")
ax.set_xticks(DEPTHS_INT)
ax.legend(); ax.yaxis.grid(True); ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig("/home/user/workspace/cs57200/charts4x4/chart3_runtime.png",
            bbox_inches="tight", pad_inches=0.05)
plt.close(); print("Chart 3 saved.")

# ═══════════════════════════════════════════════════════
# Chart 4: Solution depth distribution (A*) — violin
# ═══════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(FW, FH))

depth_data = [
    [r["depth"] for r in raw[str(sd)]["astar"] if r["found"] and r["depth"]>=0]
    for sd in DEPTHS_INT
]
positions = list(range(1, len(DEPTHS_INT)+1))
parts = ax.violinplot(depth_data, positions=positions, showmedians=True, widths=0.55)
for pc in parts["bodies"]:
    pc.set_facecolor(TEAL); pc.set_alpha(0.72)
parts["cmedians"].set_color("white"); parts["cmedians"].set_linewidth(2)
for key in ["cbars","cmins","cmaxes"]: parts[key].set_color(MUT)

for i, (dd, pos) in enumerate(zip(depth_data, positions)):
    jitter = np.random.default_rng(i).uniform(-0.08, 0.08, len(dd))
    ax.scatter(np.array([pos]*len(dd))+jitter, dd,
               color=TEAL, alpha=0.35, s=12, zorder=3)
    med = float(np.median(dd))
    ax.text(pos, med+0.5, f"med={med:.0f}", ha="center", fontsize=7.5,
            color=TEXT, weight="bold")

# 3x3 median reference line (≈21 at saturation)
ax.axhline(21, color=RUST, lw=1, linestyle=":", alpha=0.7,
           label="3×3 saturation depth (≈21)")
ax.text(len(positions)+0.3, 21, "3×3\nsat.", fontsize=7, color=RUST, va="center")

ax.set_xticks(positions)
ax.set_xticklabels([f"Scramble\n{d}" for d in DEPTHS_INT])
ax.set_ylabel("Optimal Solution Depth (moves)")
ax.set_title("Solution Depth Distribution by Scramble Level — 4×4 Puzzle")
ax.legend(fontsize=8, loc="upper left")
ax.yaxis.grid(True); ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig("/home/user/workspace/cs57200/charts4x4/chart4_depth_violin.png",
            bbox_inches="tight", pad_inches=0.05)
plt.close(); print("Chart 4 saved.")

# ═══════════════════════════════════════════════════════
# Chart 5: IDA* solve rate vs scramble depth
# ═══════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(FW, FH))

sr = [solve_rate(sd,"idastar") for sd in DEPTHS_INT]
ar = [solve_rate(sd,"astar")   for sd in DEPTHS_INT]

ax.bar([d-1.8 for d in DEPTHS_INT], ar, width=3.2, color=TEAL, alpha=0.82, label="A* solve rate")
ax.bar([d+1.8 for d in DEPTHS_INT], sr, width=3.2, color=DARK, alpha=0.82, label="IDA* solve rate")

for x, y in zip([d-1.8 for d in DEPTHS_INT], ar):
    ax.text(x, y+0.5, f"{y:.0f}%", ha="center", fontsize=8, color=TEAL, weight="bold")
for x, y in zip([d+1.8 for d in DEPTHS_INT], sr):
    ax.text(x, y+0.5, f"{y:.0f}%", ha="center", fontsize=8, color=DARK, weight="bold")

ax.axhline(100, color=MUT, lw=0.8, linestyle="--")
ax.set_ylim(0, 115)
ax.set_xlabel("Scramble Depth")
ax.set_ylabel("Solve Rate (%)")
ax.set_title("Solve Rate: A* vs IDA* — 4×4 Puzzle\n(IDA* node limit: 200K–1M per tier)")
ax.set_xticks(DEPTHS_INT)
ax.legend(); ax.yaxis.grid(True); ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig("/home/user/workspace/cs57200/charts4x4/chart5_solverate.png",
            bbox_inches="tight", pad_inches=0.05)
plt.close(); print("Chart 5 saved.")

# ── Side-by-side comparison: 3x3 vs 4x4 depth saturation ──────────────────
# Load 3x3 data too
with open("/home/user/workspace/cs57200/depth_scaling_results.json") as f:
    raw3 = json.load(f)

DEPTHS3 = [10, 20, 30, 50, 75]
DEPTHS4 = DEPTHS_INT   # [10,20,30,50]

fig, ax = plt.subplots(figsize=(FW, FH))

med3 = [float(np.median([r["depth"] for r in raw3[str(d)]["astar"]
                          if r["found"] and r["depth"]>=0])) for d in DEPTHS3]
med4 = [float(np.median([r["depth"] for r in raw[str(d)]["astar"]
                          if r["found"] and r["depth"]>=0])) for d in DEPTHS4]

ax.plot(DEPTHS3, med3, "o-", color=TEAL, lw=2.2, ms=7,
        label="3×3 (8-puzzle)  — God's number = 31")
ax.plot(DEPTHS4, med4, "s-", color=RUST, lw=2.2, ms=7,
        label="4×4 (15-puzzle) — God's number = 80")

# Saturation reference lines
ax.axhline(31, color=TEAL, lw=0.8, linestyle=":", alpha=0.6)
ax.text(max(DEPTHS3)+1, 31.5, "3×3 max (31)", fontsize=7.5, color=TEAL)
ax.axhline(80, color=RUST, lw=0.8, linestyle=":", alpha=0.6)
ax.text(max(DEPTHS3)+1, 80.5, "4×4 max (80)", fontsize=7.5, color=RUST)

for x, y in zip(DEPTHS3, med3): ax.annotate(f"{y:.0f}", (x,y), xytext=(0,6),
    textcoords="offset points", ha="center", fontsize=7.5, color=TEAL)
for x, y in zip(DEPTHS4, med4): ax.annotate(f"{y:.0f}", (x,y), xytext=(0,-14),
    textcoords="offset points", ha="center", fontsize=7.5, color=RUST)

ax.set_xlabel("Scramble Depth (random moves from goal)")
ax.set_ylabel("Median Optimal Solution Depth (moves)")
ax.set_title("Depth Saturation: 3×3 vs 4×4 Puzzle by Scramble Level")
ax.set_xticks(sorted(set(DEPTHS3+DEPTHS4)))
ax.legend(fontsize=9); ax.yaxis.grid(True); ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig("/home/user/workspace/cs57200/charts4x4/chart6_saturation_comparison.png",
            bbox_inches="tight", pad_inches=0.05)
plt.close(); print("Chart 6 saved.")

print("\nAll charts done.")
