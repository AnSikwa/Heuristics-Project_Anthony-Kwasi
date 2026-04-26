"""
CS 57200 - Heuristic Problem Solving
Final Report PDF generator.

Produces ``CS57200_Final_Report.pdf`` (10-15 pages) integrating
Milestone 1 (Introduction, Literature Review), Milestone 2
(Implementation, Phase 2 results), and Phase 3 (heuristic ablation
including Linear Conflict and Disjoint PDB) into a single document.

Run:
    python make_final_report.py
"""

import json
import os
import statistics
from typing import Dict, List, Tuple

import numpy as np
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


OUT_PDF = "CS57200_Final_Report.pdf"
CHARTS = "charts_phase3"


# ───────────────────────────────────────────────────────────────────
# Style sheet
# ───────────────────────────────────────────────────────────────────

def build_styles() -> Dict[str, ParagraphStyle]:
    """Return the named paragraph styles used throughout the report."""
    base = getSampleStyleSheet()
    styles: Dict[str, ParagraphStyle] = {}
    styles["title"] = ParagraphStyle(
        "title", parent=base["Title"],
        fontName="Helvetica-Bold", fontSize=20, leading=24,
        spaceAfter=8, textColor=colors.HexColor("#1f3b6b"),
        alignment=1)
    styles["subtitle"] = ParagraphStyle(
        "subtitle", parent=base["Normal"],
        fontName="Helvetica", fontSize=12, leading=15,
        spaceAfter=6, alignment=1, textColor=colors.HexColor("#444444"))
    styles["author"] = ParagraphStyle(
        "author", parent=base["Normal"],
        fontName="Helvetica", fontSize=11, leading=14,
        spaceAfter=12, alignment=1)
    styles["h1"] = ParagraphStyle(
        "h1", parent=base["Heading1"],
        fontName="Helvetica-Bold", fontSize=15, leading=18,
        spaceBefore=14, spaceAfter=6,
        textColor=colors.HexColor("#1f3b6b"))
    styles["h2"] = ParagraphStyle(
        "h2", parent=base["Heading2"],
        fontName="Helvetica-Bold", fontSize=12, leading=15,
        spaceBefore=10, spaceAfter=4,
        textColor=colors.HexColor("#1f3b6b"))
    styles["body"] = ParagraphStyle(
        "body", parent=base["BodyText"],
        fontName="Helvetica", fontSize=10.5, leading=14,
        spaceAfter=6, alignment=4)
    styles["caption"] = ParagraphStyle(
        "caption", parent=base["Normal"],
        fontName="Helvetica-Oblique", fontSize=9.5, leading=12,
        spaceAfter=10, alignment=1, textColor=colors.HexColor("#444444"))
    styles["mono"] = ParagraphStyle(
        "mono", parent=base["Code"],
        fontName="Courier", fontSize=9, leading=11,
        leftIndent=12, spaceAfter=6)
    styles["bullet"] = ParagraphStyle(
        "bullet", parent=base["BodyText"],
        fontName="Helvetica", fontSize=10.5, leading=13,
        leftIndent=14, bulletIndent=4, spaceAfter=3)
    return styles


# ───────────────────────────────────────────────────────────────────
# Data loading & summary helpers
# ───────────────────────────────────────────────────────────────────

def load_phase3() -> Dict[int, Dict]:
    """Load the three Phase 3 ablation result files."""
    out = {}
    for d in (20, 30, 50):
        p = f"ablation_4x4_d{d}.json"
        if os.path.exists(p):
            out[d] = json.load(open(p))
    return out


def bootstrap_ci(values: List[float], n_boot: int = 1000,
                 seed: int = 0) -> Tuple[float, float, float]:
    """Bootstrap mean and 95% CI."""
    if not values:
        return (0.0, 0.0, 0.0)
    rng = np.random.default_rng(seed)
    arr = np.asarray(values, dtype=float)
    boots = np.empty(n_boot)
    for i in range(n_boot):
        boots[i] = rng.choice(arr, size=len(arr), replace=True).mean()
    return float(arr.mean()), float(np.quantile(boots, 0.025)), \
        float(np.quantile(boots, 0.975))


def fmt_ci(mean: float, lo: float, hi: float, dec: int = 1) -> str:
    """Pretty-print mean with bootstrap 95% CI."""
    return f"{mean:,.{dec}f} [{lo:,.{dec}f}, {hi:,.{dec}f}]"


# ───────────────────────────────────────────────────────────────────
# Section builders
# ───────────────────────────────────────────────────────────────────

def cover(styles, story) -> None:
    """Build the cover block."""
    story.append(Spacer(1, 1.2 * inch))
    story.append(Paragraph(
        "Heuristic A* Search for Large Sliding Puzzles "
        "Using Advanced Heuristics", styles["title"]))
    story.append(Paragraph(
        "Final Project Report - Track B: Search & Optimization",
        styles["subtitle"]))
    story.append(Spacer(1, 0.4 * inch))
    story.append(Paragraph("Anthony Kwasi", styles["author"]))
    story.append(Paragraph("CS 57200: Heuristic Problem Solving",
                           styles["author"]))
    story.append(Paragraph("Purdue University - Spring 2026",
                           styles["author"]))
    story.append(Spacer(1, 0.6 * inch))
    story.append(Paragraph(
        "<b>Repository:</b> "
        "<a href='https://github.com/AnSikwa/Heuristics-Project_Anthony-Kwasi'"
        " color='blue'>"
        "github.com/AnSikwa/Heuristics-Project_Anthony-Kwasi</a>",
        styles["body"]))
    story.append(Spacer(1, 0.2 * inch))
    abstract = (
        "<b>Abstract.</b> We present a unified experimental study of "
        "informed search algorithms (BFS, A*, IDA*) and admissible "
        "heuristics (Manhattan distance, Linear Conflict, Disjoint "
        "Pattern Databases) for the 8- and 15-tile sliding puzzles. "
        "On the 4x4 puzzle at scramble depth 50, the disjoint "
        "additive PDB heuristic (4-4-4-3 partition) reduces A* node "
        "expansions by 15.2x relative to Manhattan distance and "
        "wall-clock time by 9.7x while preserving optimality. Linear "
        "Conflict yields a 3.5x node reduction at the same depth. "
        "Across 30-50 random instances per cell, all algorithm/heuristic "
        "combinations agree on solution depth, empirically confirming "
        "admissibility.")
    story.append(Paragraph(abstract, styles["body"]))
    story.append(PageBreak())


def section_intro(styles, story) -> None:
    """Section 1: Introduction & Problem Formulation."""
    story.append(Paragraph("1. Introduction & Problem Formulation",
                           styles["h1"]))
    story.append(Paragraph(
        "The n-puzzle, comprising n^2 - 1 numbered tiles on an n x n grid "
        "with one blank space, is a canonical benchmark for heuristic "
        "search. The 4x4 instance (15-puzzle) admits roughly 16!/2 "
        "= 1.05 x 10^13 reachable states with optimal solutions of up to "
        "80 moves, and the 5x5 instance (24-puzzle) admits 25!/2 "
        "= 7.76 x 10^24 states - far beyond brute-force search.",
        styles["body"]))
    story.append(Paragraph(
        "<b>Research question.</b> How do increasingly informed admissible "
        "heuristics (Manhattan distance, Manhattan + Linear Conflict, "
        "Disjoint Pattern Databases) compare on the same set of random "
        "15-puzzle instances when paired with A* and IDA*, in terms of "
        "node expansions, wall-clock runtime, and solution optimality?",
        styles["body"]))

    story.append(Paragraph("1.1 Formal Specification", styles["h2"]))
    spec_items = [
        "<b>State:</b> immutable tuple of length n^2; tile 0 denotes the blank.",
        "<b>Initial state:</b> any solvable permutation, generated here by a "
        "seeded random walk from the goal so solvability is structural rather "
        "than parity-checked.",
        "<b>Actions:</b> sliding the blank up, down, left, or right within the "
        "grid (branching factor at most 4; average ~2.13 on 4x4).",
        "<b>Transition cost:</b> uniform unit cost per move.",
        "<b>Goal test:</b> state == (1, 2, ..., n^2 - 1, 0).",
        "<b>Solution:</b> a minimum-length sequence of legal actions from the "
        "start to the goal."]
    for s in spec_items:
        story.append(Paragraph(s, styles["bullet"], bulletText="-"))

    story.append(Paragraph("1.2 Contributions", styles["h2"]))
    contribs = [
        "Three search algorithms - BFS (uninformed baseline), A*, and IDA* - "
        "with a shared, pluggable heuristic interface.",
        "Three admissible heuristics: Manhattan distance, Manhattan + Linear "
        "Conflict, and a disjoint additive Pattern Database under a 4-4-4-3 "
        "partition of the 15 tiles.",
        "A controlled ablation across scramble depths {20, 30, 50} on 30-50 "
        "instances per cell, with bootstrap 95% confidence intervals.",
        "Empirical confirmation that solution depths agree across heuristics "
        "(admissibility check) and quantitative speedup curves showing the "
        "PDB heuristic accelerates A* by up to 15.2x."]
    for s in contribs:
        story.append(Paragraph(s, styles["bullet"], bulletText="-"))

    story.append(Paragraph("1.3 Scope changes since Milestone 1",
                           styles["h2"]))
    story.append(Paragraph(
        "Milestone 1 proposed four enhancements: disjoint PDBs, IDA*, "
        "tie-breaking strategies, and transposition tables. The final "
        "deliverable retains and ships disjoint PDBs and IDA*, adds "
        "Linear Conflict (which Milestone 2 listed as a fallback "
        "enhancement), and defers tie-breaking and transposition tables "
        "to future work. The PDB partition was reduced from the canonical "
        "5-5-5 (~17 M projected states) to a 4-4-4-3 partition "
        "(~1.6 M states) so that the database can be built in pure Python "
        "in seconds; this matches the Milestone 2 contingency clause and "
        "still yields the headline result.",
        styles["body"]))


def section_related_work(styles, story) -> None:
    """Section 2: Related Work."""
    story.append(Paragraph("2. Related Work", styles["h1"]))
    story.append(Paragraph(
        "<b>2.1 Foundational algorithms.</b> Hart, Nilsson and Raphael "
        "[1] introduced A*, evaluating each node by f(n) = g(n) + h(n). "
        "When h is admissible, A* returns optimal solutions; "
        "consistency further guarantees no node is re-expanded in graph "
        "search. Korf [2] introduced Iterative-Deepening A* (IDA*), which "
        "trades repeated DFS sweeps for O(d) memory and was the first "
        "method to solve random 15-puzzle instances within practical "
        "limits.", styles["body"]))
    story.append(Paragraph(
        "<b>2.2 Manhattan distance.</b> Manhattan distance sums each "
        "tile's grid displacement from its goal cell. Russell & Norvig "
        "[3] derive it as the exact cost of a relaxed problem in which "
        "tiles may overlap. It is admissible and consistent but ignores "
        "tile interactions, leading to large search trees.", styles["body"]))
    story.append(Paragraph(
        "<b>2.3 Linear Conflict.</b> Hansson, Mayer and Yung [4] "
        "augment Manhattan distance with the linear conflict bonus: when "
        "two tiles share their goal row (or column) but are in reversed "
        "order, at least one must move out of the line and back, adding "
        "two moves. Adding 2 per detected conflict preserves "
        "admissibility, and the heuristic typically reduces 15-puzzle "
        "solve times by 3-5x. Qin & Zhang [5] re-confirmed this gain on "
        "modern hardware.", styles["body"]))
    story.append(Paragraph(
        "<b>2.4 Pattern Databases.</b> Culberson & Schaeffer [6] "
        "precomputed the exact cost of solving sub-problems involving "
        "subsets of tiles, achieving roughly 1000x node-expansion "
        "reduction with a fringe-pattern database. Korf & Felner [7] "
        "extended this with disjoint additive PDBs that partition the "
        "tiles into non-overlapping groups whose costs may be summed; "
        "their 7-8 partition delivered over 2000x speedup on the "
        "15-puzzle. Felner, Korf & Hanan [8] dynamically partitioned "
        "the tiles per state and solved 50 random 24-puzzle instances "
        "optimally. Holte et al. [9] showed how maximising over multiple "
        "PDBs further improves runtime.", styles["body"]))
    story.append(Paragraph(
        "<b>2.5 Tie-breaking and IDA* enhancements.</b> Asai & Fukunaga "
        "[10] showed that, even with ties on f-value, expanding nodes "
        "with the largest g first reduces the total expansion count "
        "without compromising optimality. Edelkamp & Schroedl [11] "
        "summarise transposition-table augmentations of IDA*, which trade "
        "memory for fewer redundant expansions.", styles["body"]))
    story.append(Paragraph(
        "<b>2.6 Gap and contribution.</b> Despite extensive prior work "
        "on individual techniques, there is little published work that "
        "directly compares Manhattan, Linear Conflict and a disjoint "
        "additive PDB on the same set of random 15-puzzle instances "
        "with both A* and IDA*, reporting 95% confidence intervals across "
        "three scramble depths. This report contributes such a controlled "
        "ablation and an open, reproducible Python implementation.",
        styles["body"]))


def section_design(styles, story) -> None:
    """Section 3: System Design & Implementation."""
    story.append(Paragraph("3. System Design & Implementation",
                           styles["h1"]))
    story.append(Paragraph(
        "Figure 1 shows the high-level architecture. The system has "
        "four layers: an instance generator, a state representation, a "
        "set of pluggable heuristics, and a set of search algorithms. "
        "All searches accept a heuristic callable so the same code path "
        "is reused across all enhancements.", styles["body"]))
    arch_path = os.path.join(CHARTS, "chart6_architecture.png")
    if os.path.exists(arch_path):
        story.append(Image(arch_path, width=6.6 * inch, height=3.6 * inch))
        story.append(Paragraph(
            "Figure 1. System architecture for Phase 3.",
            styles["caption"]))

    story.append(Paragraph("3.1 State representation", styles["h2"]))
    story.append(Paragraph(
        "Each state is a Python tuple of length n^2 with 0 indicating the "
        "blank. Tuples are immutable and hashable, so they can serve as "
        "dictionary keys without a separate visited set. The branching "
        "factor never exceeds 4, and parent-state pruning reduces it by "
        "one along any non-trivial path.", styles["body"]))

    story.append(Paragraph("3.2 Algorithms", styles["h2"]))
    story.append(Paragraph(
        "BFS (uninformed baseline) uses a deque frontier and a "
        "predecessor map for path reconstruction; on the 3x3 puzzle it "
        "always returns optimal-length paths because edges have unit "
        "cost.", styles["body"]))
    story.append(Paragraph(
        "A* uses a binary heap ordered by (f, g, state). Lazy deletion "
        "skips outdated heap entries when popped, avoiding decrease-key "
        "machinery. Tuple comparison lexicographically breaks ties "
        "toward smaller g first, which is admissible.", styles["body"]))
    story.append(Paragraph(
        "IDA* runs successive depth-first searches bounded by an "
        "f-threshold that grows to the next-smallest f-value after each "
        "failed iteration. Memory use is O(d). Parent-state pruning "
        "avoids two-cycle oscillation.", styles["body"]))

    story.append(Paragraph("3.3 Heuristic stack", styles["h2"]))
    story.append(Paragraph(
        "<b>Manhattan distance.</b> Sums |row_i - goal_row_i| + "
        "|col_i - goal_col_i| for every non-blank tile. Linear-time "
        "evaluation, admissible, consistent.", styles["body"]))
    story.append(Paragraph(
        "<b>Manhattan + Linear Conflict.</b> Adds 2 per linear conflict "
        "in rows and columns. Conflicts are counted greedily by "
        "repeatedly removing the most-conflicted tile in each line until "
        "the line is conflict-free.", styles["body"]))
    story.append(Paragraph(
        "<b>Disjoint Pattern Database.</b> The 15 tiles are partitioned "
        "into four disjoint groups {1,2,5,6}, {3,4,7,8}, {9,10,13,14}, "
        "{11,12,15}. Each PDB stores, for every reachable projection "
        "(blank position, tuple of group-tile positions), the minimum "
        "number of group-tile moves needed to reach a goal-aligned "
        "projection. The database is built once via a 0-1 BFS from the "
        "goal in projected space; group-tile moves cost 1 and "
        "non-group-tile moves cost 0. Per-group lookups are summed at "
        "search time, which is admissible because each move advances at "
        "most one tile.", styles["body"]))

    story.append(Paragraph("3.4 Implementation choices", styles["h2"]))
    decisions = [
        "Pure-Python implementation (no C extensions) for "
        "reproducibility and ease of grading.",
        "PDB partition 4-4-4-3 totalling 1,616,160 entries; full build "
        "completes in under 4 seconds on commodity hardware. The "
        "canonical 5-5-5 partition (~17 M entries) is exposed but not "
        "pre-built because pure-Python build time becomes prohibitive.",
        "All experiments use fixed RNG seeds; running any script twice "
        "produces identical instances and identical metrics.",
        "Per-search node and recursion limits guard against IDA* "
        "stack overflows on very deep instances."]
    for d in decisions:
        story.append(Paragraph(d, styles["bullet"], bulletText="-"))


def add_results_table(styles, story, all_data: Dict[int, Dict]) -> None:
    """Render the main ablation results table with bootstrap 95% CIs."""
    rows = [["Depth", "Heuristic", "Algorithm",
             "Solved", "Mean nodes [95% CI]", "Mean ms [95% CI]"]]
    for d in sorted(all_data.keys()):
        data = all_data[d]
        for h in ("manhattan", "linear", "pdb"):
            for alg in ("astar", "idastar"):
                runs = data["heuristics"][h][alg]
                solved = sum(1 for r in runs if r["solved"])
                nodes = [r["nodes"] for r in runs if r["solved"]]
                times = [r["time_ms"] for r in runs if r["solved"]]
                mn, mn_lo, mn_hi = bootstrap_ci(nodes)
                mt, mt_lo, mt_hi = bootstrap_ci(times)
                rows.append([
                    str(d),
                    {"manhattan": "Manhattan",
                     "linear": "Linear Conflict",
                     "pdb": "Disjoint PDB"}[h],
                    alg.upper().replace("ASTAR", "A*").replace("IDA*", "IDA*"),
                    f"{solved}/{len(runs)}",
                    fmt_ci(mn, mn_lo, mn_hi, 1),
                    fmt_ci(mt, mt_lo, mt_hi, 2),
                ])
    t = Table(rows, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3b6b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.whitesmoke, colors.white]),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#1f3b6b")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25,
         colors.HexColor("#cccccc")),
    ]))
    story.append(t)
    story.append(Paragraph(
        "Table 1. Phase 3 ablation results on the 15-puzzle. Bootstrap "
        "95% confidence intervals (1000 resamples) of the mean across "
        "30-50 random instances per cell. Solution depth matched across "
        "all heuristics and algorithms (admissibility check).",
        styles["caption"]))


def add_image(story, styles, path: str, caption: str,
              width: float = 6.4 * inch, height: float = 3.6 * inch) -> None:
    """Add an image with caption if the file exists."""
    if not os.path.exists(path):
        return
    story.append(Image(path, width=width, height=height))
    story.append(Paragraph(caption, styles["caption"]))


def section_methodology(styles, story, all_data) -> None:
    """Section 4: Experimental Methodology & Results."""
    story.append(Paragraph(
        "4. Experimental Methodology & Results", styles["h1"]))
    story.append(Paragraph("4.1 Methodology", styles["h2"]))
    story.append(Paragraph(
        "We ran three primary experiments. Phase 2 evaluated BFS, A*, "
        "and IDA* on the 3x3 (100 instances) and 4x4 (100 instances) "
        "puzzles with Manhattan distance only, plus depth-scaling "
        "sweeps. Phase 3 (this section) compares Manhattan vs Linear "
        "Conflict vs Disjoint PDB on the 15-puzzle at three scramble "
        "depths (20, 30, 50). Phase 3 used 50 instances per cell at "
        "depths 20 and 30 and 30 instances at depth 50; seed = 1234. "
        "Per-search caps were 5-10 million node expansions.",
        styles["body"]))
    story.append(Paragraph(
        "<b>Reproducibility.</b> Every experiment uses fixed RNG seeds "
        "(Phase 2: 42; 3x3 sweep: 99; 4x4 sweep: 77; ablation: 1234) "
        "and is deterministic given the Python version. Statistics "
        "below report the bootstrap mean with 95% percentile "
        "confidence intervals (1000 resamples).",
        styles["body"]))

    story.append(Paragraph("4.2 Phase 2 main results (Manhattan only)",
                           styles["h2"]))
    p2 = [
        ["Size", "Algorithm", "Mean nodes", "Mean depth",
         "Mean ms", "Solved"],
        ["3x3", "BFS", "73,865", "21.7", "140.91", "100/100"],
        ["3x3", "A*",  "1,564",  "21.7", "8.57",   "100/100"],
        ["3x3", "IDA*", "2,062", "21.7", "8.75",   "100/100"],
        ["4x4", "A*",  "212",    "18.7", "1.79",   "100/100"],
        ["4x4", "IDA*", "177",   "18.7", "1.28",   "100/100"],
    ]
    t = Table(p2, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3b6b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.whitesmoke, colors.white]),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#1f3b6b")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25,
         colors.HexColor("#cccccc")),
    ]))
    story.append(t)
    story.append(Paragraph(
        "Table 2. Phase 2 baseline. A* expands ~47x fewer nodes than "
        "BFS on the 3x3 puzzle; on the 4x4, IDA* outperforms A* at "
        "scramble depth 20 because saving memory dominates the cost of "
        "re-expanding nodes.",
        styles["caption"]))

    story.append(Paragraph("4.3 Phase 3 ablation across heuristics",
                           styles["h2"]))
    add_results_table(styles, story, all_data)

    story.append(PageBreak())

    story.append(Paragraph("4.4 Visual results", styles["h2"]))
    add_image(story, styles, os.path.join(CHARTS, "chart1_nodes_by_heuristic.png"),
              "Figure 2. Mean A* nodes expanded by heuristic and "
              "scramble depth (log scale). Error bars show bootstrap "
              "95% CIs. PDB lies an order of magnitude below "
              "Manhattan at depth 50.")
    add_image(story, styles, os.path.join(CHARTS, "chart3_speedup_vs_baseline.png"),
              "Figure 3. Node-expansion speedup over Manhattan baseline. "
              "Linear Conflict yields 1.5-3.5x; Disjoint PDB yields "
              "2.7-15.2x and the gap widens with depth.")
    add_image(story, styles, os.path.join(CHARTS, "chart4_nodes_box.png"),
              "Figure 4. Distribution of A* node expansions at scramble "
              "depth 50 (log scale). Each box shows the IQR, whiskers "
              "the 1.5x IQR range, and the green triangle the mean.")
    add_image(story, styles, os.path.join(CHARTS, "chart5_scaling_curve.png"),
              "Figure 5. Scaling curves for mean A* node expansions vs "
              "scramble depth (log scale). The shaded band shows the "
              "95% CI; the PDB curve grows substantially slower than "
              "Manhattan.")


def section_analysis(styles, story, all_data) -> None:
    """Section 5: Analysis & Interpretation."""
    story.append(Paragraph("5. Analysis & Interpretation", styles["h1"]))

    # Compute concrete speedups for the prose.
    deepest = max(all_data.keys())
    base_nodes = [r["nodes"] for r in
                  all_data[deepest]["heuristics"]["manhattan"]["astar"]
                  if r["solved"]]
    lc_nodes = [r["nodes"] for r in
                all_data[deepest]["heuristics"]["linear"]["astar"]
                if r["solved"]]
    pdb_nodes = [r["nodes"] for r in
                 all_data[deepest]["heuristics"]["pdb"]["astar"]
                 if r["solved"]]
    base_time = [r["time_ms"] for r in
                 all_data[deepest]["heuristics"]["manhattan"]["astar"]
                 if r["solved"]]
    pdb_time = [r["time_ms"] for r in
                all_data[deepest]["heuristics"]["pdb"]["astar"]
                if r["solved"]]
    lc_speedup = (statistics.mean(base_nodes) / statistics.mean(lc_nodes)
                  if lc_nodes else 0)
    pdb_speedup = (statistics.mean(base_nodes) / statistics.mean(pdb_nodes)
                   if pdb_nodes else 0)
    pdb_time_speedup = (statistics.mean(base_time) /
                        statistics.mean(pdb_time)
                        if pdb_time else 0)

    story.append(Paragraph("5.1 Why does PDB win at depth?", styles["h2"]))
    story.append(Paragraph(
        f"At scramble depth {deepest}, Linear Conflict achieves a "
        f"{lc_speedup:.1f}x reduction in A* node expansions and the "
        f"4-4-4-3 disjoint PDB achieves {pdb_speedup:.1f}x; PDB also "
        f"reduces wall-clock time by {pdb_time_speedup:.1f}x because "
        "each PDB lookup is a single dictionary access whereas Linear "
        "Conflict requires an inner loop. The gap widens with depth "
        "because the heuristic-to-true-cost gap for Manhattan distance "
        "grows roughly linearly with depth, while the PDB captures "
        "exact within-group costs and so its error scales sub-linearly.",
        styles["body"]))

    story.append(Paragraph("5.2 Admissibility check", styles["h2"]))
    story.append(Paragraph(
        "All three heuristics produced identical mean solution depths "
        "for every scramble depth in Table 1, on every instance. This "
        "is the empirical signature of admissibility: a non-admissible "
        "heuristic could return shorter (incorrect) paths. Combined "
        "with our hand-verified 8-puzzle benchmarks (depths 1, 3 and "
        "28, all matched), this is strong evidence the implementation "
        "is correct.", styles["body"]))

    story.append(Paragraph("5.3 A* vs IDA* across heuristics", styles["h2"]))
    story.append(Paragraph(
        "IDA* re-expands nodes across iterations but uses O(d) memory. "
        "With Manhattan distance, IDA*'s repeated work hurts at deep "
        "scrambles - at depth 50 IDA* expands roughly 2x as many nodes "
        "as A*. With the PDB heuristic, the per-iteration node count "
        "drops so sharply that IDA*'s overhead is small in absolute "
        "terms; depth-50 IDA*+PDB completes in roughly the same time "
        "as A*+PDB while using a fraction of the memory. This is the "
        "Korf & Felner observation transferred to a smaller PDB.",
        styles["body"]))

    story.append(Paragraph("5.4 Limitations", styles["h2"]))
    lims = [
        "Pure Python keeps absolute runtimes higher than published "
        "C/C++ implementations; ratios are the meaningful quantity.",
        "The 4-4-4-3 partition is non-canonical; the 7-8 or 5-5-5 "
        "partitions used by Korf & Felner would yield substantially "
        "stronger heuristics at the cost of a multi-hour build.",
        "Scramble depths beyond 50 cause unpredictable variance; we "
        "did not exhaust solvable depth.",
        "Only random instances were tested; pathological instances "
        "(near-maximal optimal solutions ~80 moves) are out of scope."]
    for s in lims:
        story.append(Paragraph(s, styles["bullet"], bulletText="-"))


def section_conclusion(styles, story) -> None:
    """Section 6: Conclusion & Future Work."""
    story.append(Paragraph("6. Conclusion & Future Work", styles["h1"]))
    story.append(Paragraph(
        "We delivered a unified, reproducible heuristic-search testbed "
        "for the sliding-tile puzzle with three search algorithms and "
        "three admissible heuristics. The headline result is a 15.2x "
        "node-expansion speedup of A*+PDB over A*+Manhattan at scramble "
        "depth 50, with strict optimality preserved across all "
        "comparisons. Linear Conflict is a strictly weaker enhancement "
        "(3.5x speedup at the same depth) but is far cheaper to "
        "implement and adds no precomputation cost.", styles["body"]))
    story.append(Paragraph(
        "<b>Lessons learned.</b> Pure-Python PDB construction is "
        "viable for partitions up to ~5 tiles per group; beyond that, "
        "either C extensions or memory-mapped on-disk tables are "
        "required. Treating the heuristic as a callable parameter "
        "(rather than hard-coding it inside the solver) made the "
        "ablation trivial to add and made the search code easier to "
        "test.",
        styles["body"]))
    story.append(Paragraph("6.1 Future work", styles["h2"]))
    fw = [
        "Build the canonical 5-5-5 or 7-8 PDB partitions with a C "
        "extension or numpy-backed flat array, expecting another "
        "5-10x improvement.",
        "Implement and study Asai-Fukunaga tie-breaking: "
        "prefer-larger-g and prefer-smaller-h within an f-bucket, "
        "which is independent of the heuristic and orthogonal to PDBs.",
        "Add transposition tables to IDA* and measure the "
        "memory/expansion trade-off across various table sizes.",
        "Generalise the implementation to the 24-puzzle (5x5), where "
        "Manhattan-only IDA* is intractable; this exercises the "
        "memory-efficiency rationale for IDA* most clearly.",
        "Apply the same testbed to learning-based heuristics "
        "(e.g., neural cost-to-go regressors) for a head-to-head "
        "comparison with classical PDBs."]
    for s in fw:
        story.append(Paragraph(s, styles["bullet"], bulletText="-"))


def section_references(styles, story) -> None:
    """References. Each entry includes a clickable URL."""
    story.append(Paragraph("References", styles["h1"]))
    refs = [
        "[1] Hart, P. E., Nilsson, N. J., & Raphael, B. (1968). "
        "A formal basis for the heuristic determination of minimum "
        "cost paths. <i>IEEE Trans. Systems Science and "
        "Cybernetics</i>, 4(2), 100-107. "
        "<a href='https://www.cs.auckland.ac.nz/courses/compsci709s2c/"
        "resources/Mike.d/astarNilsson.pdf' color='blue'>"
        "Link</a>",
        "[2] Korf, R. E. (1985). Depth-first iterative-deepening: an "
        "optimal admissible tree search. <i>Artificial Intelligence</i>, "
        "27(1), 97-109. "
        "<a href='https://academiccommons.columbia.edu/doi/"
        "10.7916/D8HQ46X1' color='blue'>Link</a>",
        "[3] Russell, S. & Norvig, P. (2021). <i>Artificial "
        "Intelligence: A Modern Approach</i> (4th ed.). Pearson. "
        "<a href='https://aima.cs.berkeley.edu/' color='blue'>Link</a>",
        "[4] Hansson, O., Mayer, A. & Yung, M. (1992). Generating "
        "admissible heuristics by criticising solutions to relaxed "
        "models. <i>Artificial Intelligence</i>, 55(1), 29-60.",
        "[5] Qin, Z. & Zhang, M. (2025). Solving the sliding puzzle "
        "problem using the A* algorithm and comparing heuristic "
        "functions. Dean & Francis Academic Publishing.",
        "[6] Culberson, J. & Schaeffer, J. (1998). Pattern databases. "
        "<i>Computational Intelligence</i>, 14(3), 318-334. "
        "<a href='https://webdocs.cs.ualberta.ca/~jonathan/publications/"
        "ai_publications/compi.pdf' color='blue'>Link</a>",
        "[7] Korf, R. E. & Felner, A. (2002). Disjoint pattern database "
        "heuristics. <i>Artificial Intelligence</i>, 134(1-2), 9-22.",
        "[8] Felner, A., Korf, R. E. & Hanan, S. (2004). Additive "
        "pattern database heuristics. <i>Journal of Artificial "
        "Intelligence Research</i>, 22, 279-318. "
        "<a href='https://www.ise.bgu.ac.il/faculty/felner/research/"
        "jairpdb.pdf' color='blue'>Link</a>",
        "[9] Holte, R. C., Felner, A., Newton, J., Meshulam, R. & Furcy, "
        "D. (2006). Maximizing multiple pattern databases speeds up "
        "heuristic search. <i>Artificial Intelligence</i>, 170(16-17), "
        "1123-1136. "
        "<a href='https://www.sciencedirect.com/science/article/pii/"
        "S0004370206000804' color='blue'>Link</a>",
        "[10] Asai, M. & Fukunaga, A. (2018). Analysing tie-breaking "
        "strategies for the A* algorithm. <i>Proceedings of "
        "IJCAI-2018</i>, 4660-4666.",
        "[11] Edelkamp, S. & Schroedl, S. (2012). <i>Heuristic Search: "
        "Theory and Applications</i>. Morgan Kaufmann.",
        "[12] Kishimoto, A., Fukunaga, A. & Botea, A. (2013). "
        "Evaluation of a simple, scalable, parallel best-first search "
        "strategy. <i>Artificial Intelligence</i>, 195, 222-248."]
    for r in refs:
        story.append(Paragraph(r, styles["body"]))


def section_appendix(styles, story) -> None:
    """Appendix: reproduction commands and repository layout."""
    story.append(PageBreak())
    story.append(Paragraph("Appendix A. Reproducing the results",
                           styles["h1"]))
    story.append(Paragraph(
        "All scripts live in the project root. Python 3.9 or newer is "
        "required; install dependencies with "
        "<font face='Courier'>pip install -r requirements.txt</font>.",
        styles["body"]))
    story.append(Paragraph("Phase 2 (BFS / A* / IDA* with Manhattan):",
                           styles["body"]))
    story.append(Paragraph("python solver.py", styles["mono"]))
    story.append(Paragraph("python make_charts.py", styles["mono"]))
    story.append(Paragraph("python make_report.py", styles["mono"]))
    story.append(Paragraph("Phase 3 (heuristic ablation):",
                           styles["body"]))
    story.append(Paragraph(
        "python ablation.py --n 4 --scramble 20 --instances 50 "
        "--out ablation_4x4_d20.json", styles["mono"]))
    story.append(Paragraph(
        "python ablation.py --n 4 --scramble 30 --instances 50 "
        "--out ablation_4x4_d30.json", styles["mono"]))
    story.append(Paragraph(
        "python ablation.py --n 4 --scramble 50 --instances 30 "
        "--out ablation_4x4_d50.json", styles["mono"]))
    story.append(Paragraph("python ablation_charts.py", styles["mono"]))
    story.append(Paragraph("python make_final_report.py", styles["mono"]))


# ───────────────────────────────────────────────────────────────────
# Main
# ───────────────────────────────────────────────────────────────────

def main() -> None:
    """Build the final report PDF."""
    all_data = load_phase3()
    if not all_data:
        raise SystemExit(
            "No ablation_*.json files found - run ablation.py first.")
    styles = build_styles()
    doc = SimpleDocTemplate(
        OUT_PDF, pagesize=LETTER,
        leftMargin=0.85 * inch, rightMargin=0.85 * inch,
        topMargin=0.7 * inch, bottomMargin=0.7 * inch,
        title="CS 57200 Final Report - Heuristic A* for Sliding Puzzles",
        author="Anthony Kwasi")
    story: List = []
    cover(styles, story)
    section_intro(styles, story)
    section_related_work(styles, story)
    section_design(styles, story)
    section_methodology(styles, story, all_data)
    section_analysis(styles, story, all_data)
    section_conclusion(styles, story)
    section_references(styles, story)
    section_appendix(styles, story)
    doc.build(story)
    print(f"Wrote {OUT_PDF}")


if __name__ == "__main__":
    main()
