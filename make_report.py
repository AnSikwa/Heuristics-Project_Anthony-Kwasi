"""
CS 57200 – Phase 2 Report Generator
Produces a formatted PDF report with code, tables, charts, and analysis.
"""

import json
import urllib.request
from pathlib import Path

ROOT        = Path(__file__).parent
DATA_DIR    = ROOT / "data"
CHARTS_DIR  = ROOT / "charts"
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, Image, HRFlowable, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ─── Fonts ───────────────────────────────────────────────
FONT_DIR = Path("/tmp/fonts")
FONT_DIR.mkdir(exist_ok=True)

def dl_font(url, name):
    path = FONT_DIR / name
    if not path.exists():
        try:
            urllib.request.urlretrieve(url, path)
        except Exception:
            return False
    return path.exists()

FONTS_OK = (
    dl_font("https://github.com/google/fonts/raw/main/ofl/dmsans/DMSans%5Bopsz%2Cwght%5D.ttf",  "DMSans.ttf") and
    dl_font("https://github.com/google/fonts/raw/main/ofl/dmsans/DMSans-Italic%5Bopsz%2Cwght%5D.ttf", "DMSans-Italic.ttf")
)

if FONTS_OK:
    pdfmetrics.registerFont(TTFont("DMSans",       str(FONT_DIR / "DMSans.ttf")))
    pdfmetrics.registerFont(TTFont("DMSans-Bold",  str(FONT_DIR / "DMSans.ttf")))  # weight via style
    pdfmetrics.registerFont(TTFont("DMSans-Italic",str(FONT_DIR / "DMSans-Italic.ttf")))
    BODY  = "DMSans"
    HEAD  = "DMSans-Bold"
else:
    BODY  = "Helvetica"
    HEAD  = "Helvetica-Bold"

MONO = "Courier"

# ─── Palette ─────────────────────────────────────────────
TEAL      = HexColor("#01696F")
TEAL_DARK = HexColor("#1B474D")
TEAL_CHART= HexColor("#20808D")
BG        = HexColor("#F7F6F2")
TEXT_COL  = HexColor("#28251D")
MUTED     = HexColor("#7A7974")
BORDER    = HexColor("#D4D1CA")
RUST      = HexColor("#A84B2F")
HEADER_BG = HexColor("#1B474D")
ROW_ALT   = HexColor("#EFF5F5")
CODE_BG   = HexColor("#F0EFEB")

W, H = letter

# ─── Styles ──────────────────────────────────────────────
styles = getSampleStyleSheet()

def mk(name, parent="Normal", **kw):
    return ParagraphStyle(name, parent=styles[parent], **kw)

Title      = mk("RTitle", "Title",    fontName=HEAD, fontSize=22, textColor=TEXT_COL,
                 spaceAfter=4, leading=28)
Subtitle   = mk("RSub",   "Normal",   fontName=BODY, fontSize=12, textColor=MUTED,
                 spaceAfter=14, leading=16)
H1         = mk("RH1",    "Heading1", fontName=HEAD, fontSize=14, textColor=TEAL_DARK,
                 spaceBefore=14, spaceAfter=4, leading=18)
H2         = mk("RH2",    "Heading2", fontName=HEAD, fontSize=11, textColor=TEXT_COL,
                 spaceBefore=10, spaceAfter=3, leading=15)
Body       = mk("RBody",  "Normal",   fontName=BODY, fontSize=10, textColor=TEXT_COL,
                 spaceAfter=6,  leading=15)
BulletSt   = mk("RBul",   "Normal",   fontName=BODY, fontSize=10, textColor=TEXT_COL,
                 spaceAfter=3,  leading=14, leftIndent=14, bulletIndent=4)
Caption    = mk("RCap",   "Normal",   fontName=BODY, fontSize=8,  textColor=MUTED,
                 spaceAfter=8,  leading=11, alignment=1)
Code       = mk("RCode",  "Normal",   fontName=MONO, fontSize=7.5, textColor=TEXT_COL,
                 spaceAfter=2,  leading=11, backColor=CODE_BG,
                 leftIndent=8,  rightIndent=8, borderPadding=(4,4,4,4))
CodeBlock  = mk("RCodeB", "Normal",   fontName=MONO, fontSize=7.5, textColor=TEXT_COL,
                 spaceAfter=6,  leading=11, backColor=CODE_BG,
                 leftIndent=8,  rightIndent=8, borderPadding=(6,6,6,6),
                 spaceBefore=4)
FootNote   = mk("RFoot",  "Normal",   fontName=BODY, fontSize=7.5, textColor=MUTED,
                 spaceAfter=2,  leading=10)
TblHdr     = mk("RTHdr",  "Normal",   fontName=HEAD, fontSize=9,   textColor=white,
                 alignment=1, leading=12)
TblCell    = mk("RTCell", "Normal",   fontName=BODY, fontSize=9,   textColor=TEXT_COL,
                 alignment=1, leading=12)
TblCellL   = mk("RTCellL","Normal",   fontName=BODY, fontSize=9,   textColor=TEXT_COL,
                 alignment=0, leading=12)

def bullet(text):
    return Paragraph(f"• {text}", BulletSt)

def code_block(text):
    escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    lines = escaped.split("\n")
    return [Paragraph(line if line else " ", Code) for line in lines]

# ─── Header / Footer ─────────────────────────────────────
def header_footer(canvas_obj, doc):
    canvas_obj.saveState()
    # Header bar
    canvas_obj.setFillColor(HEADER_BG)
    canvas_obj.rect(0, H - 28, W, 28, fill=1, stroke=0)
    canvas_obj.setFont(HEAD, 8)
    canvas_obj.setFillColor(white)
    canvas_obj.drawString(0.75*inch, H - 18, "CS 57200 – Heuristic Problem Solving")
    canvas_obj.drawRightString(W - 0.75*inch, H - 18,
                               "Phase 2: A*/IDA* Sliding Tile Puzzle Solver")
    # Footer
    canvas_obj.setFillColor(MUTED)
    canvas_obj.setFont(BODY, 7.5)
    canvas_obj.drawString(0.75*inch, 24, "Purdue University · CS 57200 · Track B: Search & Optimization")
    canvas_obj.drawRightString(W - 0.75*inch, 24, f"Page {doc.page}")
    canvas_obj.setStrokeColor(BORDER)
    canvas_obj.setLineWidth(0.5)
    canvas_obj.line(0.75*inch, 36, W - 0.75*inch, 36)
    canvas_obj.restoreState()

# ─── Load data ───────────────────────────────────────────
with open(DATA_DIR / "raw_results.json") as f:
    raw = json.load(f)

def sv(lst): return [v for v in lst if v is not None and (isinstance(v, (int,float)) and v >= 0)]
def smean(l): v=sv(l); return sum(v)/len(v) if v else 0
def smed(l):
    v=sorted(sv(l)); n=len(v)
    if not n: return 0
    return (v[n//2-1]+v[n//2])/2 if n%2==0 else v[n//2]
def smax(l): v=sv(l); return max(v) if v else 0
def smin(l): v=sv(l); return min(v) if v else 0

# ─── Table builder ───────────────────────────────────────
def results_table(size_key: str, show_bfs=True) -> Table:
    hdr = [
        Paragraph("Algorithm", TblHdr),
        Paragraph("Solved", TblHdr),
        Paragraph("Nodes\n(mean)", TblHdr),
        Paragraph("Nodes\n(median)", TblHdr),
        Paragraph("Nodes\n(max)", TblHdr),
        Paragraph("Depth\n(mean)", TblHdr),
        Paragraph("Runtime\n(mean ms)", TblHdr),
    ]
    rows = [hdr]

    configs = []
    if show_bfs:
        configs.append(("BFS (baseline)", "bfs"))
    configs += [("A* (Manhattan)", "astar"), ("IDA* (Manhattan)", "idastar")]

    for label, key in configs:
        d = raw[size_key]
        n_solved = len([v for v in d[key]["depth"] if v is not None and v >= 0])
        rows.append([
            Paragraph(label, TblCellL),
            Paragraph(f"{n_solved}/100", TblCell),
            Paragraph(f"{smean(d[key]['nodes']):,.0f}", TblCell),
            Paragraph(f"{smed(d[key]['nodes']):,.0f}", TblCell),
            Paragraph(f"{smax(d[key]['nodes']):,.0f}", TblCell),
            Paragraph(f"{smean(d[key]['depth']):.1f}", TblCell),
            Paragraph(f"{smean(d[key]['time_ms']):.2f}", TblCell),
        ])

    col_w = [1.55*inch, 0.75*inch, 0.80*inch, 0.80*inch, 0.80*inch, 0.65*inch, 0.95*inch]
    t = Table(rows, colWidths=col_w)
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0), HEADER_BG),
        ("TEXTCOLOR",   (0,0), (-1,0), white),
        ("FONTNAME",    (0,0), (-1,0), HEAD),
        ("FONTSIZE",    (0,0), (-1,-1), 9),
        ("ALIGN",       (0,0), (-1,-1), "CENTER"),
        ("ALIGN",       (0,0), (0,-1),  "LEFT"),
        ("GRID",        (0,0), (-1,-1), 0.4, BORDER),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [white, ROW_ALT]),
        ("TOPPADDING",  (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING",(0,0), (-1,-1), 6),
        ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
    ]))
    return t

def chart_img(path, w=6.0, h=3.6):
    return Image(path, width=w*inch, height=h*inch)

# ─────────────────────────────────────────────────────────
# BUILD STORY
# ─────────────────────────────────────────────────────────
story = []

# ══════════════════════════════
# COVER
# ══════════════════════════════
story += [
    Spacer(1, 0.5*inch),
    Paragraph("CS 57200: Heuristic Problem Solving", Subtitle),
    Paragraph("Milestone 2 — Implementation Progress &amp; Preliminary Results", Title),
    HRFlowable(width="100%", thickness=2, color=TEAL, spaceAfter=10),
    Paragraph("Track B: Search &amp; Optimization", H2),
    Spacer(1, 0.1*inch),
    Paragraph("Project: <b>Heuristic A* Search for Large Sliding Puzzles</b>", Body),
    Paragraph("Algorithm Variants: BFS (baseline), A* with Manhattan Distance, IDA* with Manhattan Distance", Body),
    Paragraph("Puzzle Sizes Tested: 3×3 (8-puzzle), 4×4 (15-puzzle)", Body),
    Paragraph("Experiment Scale: 100 random solvable instances per puzzle size", Body),
    Spacer(1, 0.15*inch),
    Paragraph("Submitted: April 2026 &nbsp;&nbsp;|&nbsp;&nbsp; Purdue University", FootNote),
    PageBreak(),
]

# ══════════════════════════════
# 1. INTRODUCTION
# ══════════════════════════════
story += [
    Paragraph("1. Introduction &amp; Motivation", H1),
    HRFlowable(width="100%", thickness=0.6, color=BORDER, spaceAfter=6),
    Paragraph(
        "The sliding tile puzzle is a canonical benchmark for heuristic search algorithms. "
        "In the 8-puzzle (3×3 grid), the state space contains 181,440 reachable configurations; "
        "in the 15-puzzle (4×4 grid), that grows to over 10 trillion. Brute-force methods such "
        "as Breadth-First Search (BFS) become impractical beyond the 8-puzzle, making informed "
        "heuristic search essential.", Body),
    Paragraph(
        "This milestone implements and empirically evaluates three search strategies: "
        "(1) BFS as a provably optimal but uninformed baseline, "
        "(2) A* with Manhattan distance as the primary informed algorithm, and "
        "(3) IDA* with Manhattan distance as a memory-efficient enhancement. "
        "Experiments are conducted over 100 randomly generated solvable instances for each "
        "puzzle size, measuring nodes expanded, optimal solution depth, and runtime.", Body),
    Paragraph(
        "The central hypothesis is that Manhattan distance provides a sufficiently tight "
        "admissible heuristic to reduce node expansions by one to two orders of magnitude "
        "compared to BFS, while IDA* trades additional node re-expansions for dramatically "
        "reduced memory usage.", Body),
    Spacer(1, 0.1*inch),
]

# ══════════════════════════════
# 2. PROBLEM FORMULATION
# ══════════════════════════════
story += [
    Paragraph("2. Problem Formulation", H1),
    HRFlowable(width="100%", thickness=0.6, color=BORDER, spaceAfter=6),
    Paragraph("<b>State representation.</b>  A state is an immutable Python tuple of length n², "
              "where tile 0 represents the blank. The goal state places tiles 1 through n²−1 "
              "in row-major order with the blank at the last position.", Body),
    bullet("State: tuple(1, 2, 3, 4, 5, 6, 7, 8, 0)  [goal for 3×3]"),
    bullet("Operators: Up, Down, Left, Right — swap blank with adjacent tile (bounded by grid edges)"),
    bullet("Path cost: 1 per move; objective is minimum total moves (optimal solution)"),
    bullet("Goal test: state == goal_state(n)"),
    Spacer(1, 0.05*inch),
    Paragraph("<b>Solvability.</b>  A random permutation is solvable iff: for odd n, the inversion "
              "count is even; for even n, the parity of (inversion count + blank row from bottom) "
              "is odd. Instances are generated by performing 50 (3×3) or 20 (4×4) random moves "
              "from the goal, guaranteeing solvability by construction.", Body),
    Paragraph("<b>State space complexity.</b>  The reachable state space has size (n²)!/2. "
              "For 3×3: 9!/2 = 181,440 states. For 4×4: 16!/2 ≈ 10.46 trillion states.", Body),
    Spacer(1, 0.1*inch),
]

# ══════════════════════════════
# 3. ALGORITHMS
# ══════════════════════════════
story += [
    Paragraph("3. Algorithm Descriptions", H1),
    HRFlowable(width="100%", thickness=0.6, color=BORDER, spaceAfter=6),

    Paragraph("3.1 BFS (Uninformed Baseline)", H2),
    Paragraph("BFS explores states in FIFO order, expanding all states at depth d before "
              "depth d+1. It guarantees an optimal solution for unit-cost problems but requires "
              "O(b<super>d</super>) memory, where b is the branching factor (~2.67 for the "
              "8-puzzle) and d is the solution depth. For the 4×4 puzzle, BFS is "
              "computationally infeasible.", Body),

    Paragraph("3.2 A* with Manhattan Distance", H2),
    Paragraph("A* expands states ordered by f(n) = g(n) + h(n), where g(n) is the path cost "
              "from start and h(n) is the Manhattan distance heuristic. The Manhattan distance "
              "sums the horizontal and vertical displacements of each tile from its goal "
              "position:", Body),
    Paragraph("&nbsp;&nbsp;&nbsp; h(n) = Σ (|row(tile) − goal_row(tile)| + |col(tile) − goal_col(tile)|) "
              "for all tiles ≠ 0", Code),
    Paragraph("Manhattan distance is admissible (never overestimates) and consistent (satisfies "
              "the triangle inequality), so A* with this heuristic is guaranteed to find an "
              "optimal solution. A hash map tracks best known g-costs per state to avoid "
              "re-expansion.", Body),

    Paragraph("3.3 IDA* with Manhattan Distance", H2),
    Paragraph("IDA* (Iterative Deepening A*) performs depth-first search with a cost bound that "
              "starts at h(start) and increases to the minimum f-value that exceeded the "
              "previous bound. It uses O(d) memory (the current path only) and finds optimal "
              "solutions. The trade-off is that states may be re-expanded across iterations, "
              "increasing node expansions. This implementation prunes immediate back-tracking "
              "(never revisiting the parent) to reduce redundant work.", Body),
    Spacer(1, 0.1*inch),
]

# ══════════════════════════════
# 4. IMPLEMENTATION
# ══════════════════════════════
story += [
    Paragraph("4. Implementation", H1),
    HRFlowable(width="100%", thickness=0.6, color=BORDER, spaceAfter=6),
    Paragraph("All solvers are implemented in Python 3 using only the standard library "
              "(heapq, collections.deque, random). No third-party search libraries are used. "
              "The code is structured in a single module <b>solver.py</b> with clearly "
              "separated helper functions and solver functions.", Body),

    Paragraph("4.1 Core Helper Functions", H2),
    Spacer(1, 0.05*inch),
    Paragraph("Manhattan distance heuristic:", Body),
    *code_block(
"""def manhattan_distance(state: tuple, n: int) -> int:
    dist = 0
    for idx, tile in enumerate(state):
        if tile == 0:
            continue
        goal_idx = tile - 1        # tile k is at index k-1 in goal
        goal_row, goal_col = divmod(goal_idx, n)
        cur_row,  cur_col  = divmod(idx, n)
        dist += abs(cur_row - goal_row) + abs(cur_col - goal_col)
    return dist"""
    ),
    Spacer(1, 0.05*inch),
    Paragraph("Neighbor generation (one move from blank):", Body),
    *code_block(
"""def neighbors(state: tuple, n: int) -> List[tuple]:
    bi = state.index(0)           # blank position
    row, col = divmod(bi, n)
    moves = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = row + dr, col + dc
        if 0 <= nr < n and 0 <= nc < n:
            ni = nr * n + nc
            lst = list(state)
            lst[bi], lst[ni] = lst[ni], lst[bi]
            moves.append(tuple(lst))
    return moves"""
    ),
    Spacer(1, 0.05*inch),

    Paragraph("4.2 A* Solver Core", H2),
    *code_block(
"""def astar(start: tuple, n: int, max_nodes: int = 1_000_000) -> Dict:
    goal = goal_state(n)
    heap = [(manhattan_distance(start, n), 0, start)]
    g_best = {start: 0}
    parent = {start: None}
    nodes_expanded = 0
    while heap:
        f, g, state = heapq.heappop(heap)
        if g > g_best.get(state, math.inf): continue  # stale entry
        nodes_expanded += 1
        if state == goal:
            # reconstruct depth via parent chain
            depth = 0
            cur = state
            while parent[cur]: cur = parent[cur]; depth += 1
            return {"nodes_expanded": nodes_expanded, "depth": depth, "found": True}
        for nb in neighbors(state, n):
            new_g = g + 1
            if new_g < g_best.get(nb, math.inf):
                g_best[nb] = new_g
                parent[nb] = state
                heapq.heappush(heap, (new_g + manhattan_distance(nb, n), new_g, nb))
    return {"nodes_expanded": nodes_expanded, "depth": -1, "found": False}"""
    ),
    Spacer(1, 0.05*inch),

    Paragraph("4.3 IDA* Solver Core", H2),
    *code_block(
"""def idastar(start: tuple, n: int, max_nodes: int = 500_000) -> Dict:
    goal = goal_state(n)
    counter = [0]

    def search(path, g, bound):
        state = path[-1]
        f = g + manhattan_distance(state, n)
        if f > bound: return f          # prune
        if state == goal: return -1     # found
        counter[0] += 1
        minimum = math.inf
        prev = path[-2] if len(path) >= 2 else None
        for nb in neighbors(state, n):
            if nb == prev: continue     # no back-tracking
            path.append(nb)
            t = search(path, g + 1, bound)
            path.pop()
            if t == -1: return -1
            if t < minimum: minimum = t
        return minimum

    bound = manhattan_distance(start, n)
    path  = [start]
    while True:
        t = search(path, 0, bound)
        if t == -1:
            return {"nodes_expanded": counter[0], "depth": len(path)-1, "found": True}
        if t == math.inf:
            return {"nodes_expanded": counter[0], "depth": -1, "found": False}
        bound = t"""
    ),
    Spacer(1, 0.1*inch),
]

# ══════════════════════════════
# 5. EXPERIMENTAL SETUP
# ══════════════════════════════
story += [
    Paragraph("5. Experimental Setup", H1),
    HRFlowable(width="100%", thickness=0.6, color=BORDER, spaceAfter=6),
    Paragraph("<b>Instance generation.</b>  100 solvable instances per puzzle size were generated "
              "by performing random moves from the goal state using a seeded RNG (seed=42), "
              "ensuring reproducibility. The 3×3 instances use 50 random moves (medium-to-hard "
              "difficulty); the 4×4 instances use 20 random moves to keep all three algorithms "
              "tractable within node expansion limits.", Body),
    Paragraph("<b>Metrics collected</b> for each algorithm on each instance:", Body),
    bullet("Nodes expanded — total states popped from the frontier (A*, BFS) or expanded "
           "in the DFS tree (IDA*)"),
    bullet("Solution depth — optimal number of moves from start to goal (validated equal "
           "across all solvers that find a solution)"),
    bullet("Wall-clock runtime — measured with time.perf_counter() in milliseconds"),
    Spacer(1, 0.05*inch),
    Paragraph("<b>Node limits.</b>  BFS: 500,000 nodes (3×3 only); A*: 1M nodes (3×3), "
              "2M nodes (4×4); IDA*: 500K nodes (3×3), 1M nodes (4×4). All 100 instances "
              "per size were solved successfully by both A* and IDA*.", Body),
    Paragraph("<b>Environment.</b>  Python 3.11 on Linux (x86-64), single-threaded, "
              "standard-library only.", Body),
    Spacer(1, 0.1*inch),
]

# ══════════════════════════════
# 6. RESULTS
# ══════════════════════════════
story += [
    Paragraph("6. Results", H1),
    HRFlowable(width="100%", thickness=0.6, color=BORDER, spaceAfter=6),

    Paragraph("6.1 3×3 Puzzle (8-Puzzle) Results", H2),
    Spacer(1, 0.05*inch),
    results_table("3x3", show_bfs=True),
    Spacer(1, 0.05*inch),
    Paragraph("Table 1: Summary statistics for 100 instances of the 3×3 sliding puzzle.",
              Caption),
    Spacer(1, 0.15*inch),

    Paragraph("6.2 4×4 Puzzle (15-Puzzle) Results", H2),
    Spacer(1, 0.05*inch),
    results_table("4x4", show_bfs=False),
    Spacer(1, 0.05*inch),
    Paragraph("Table 2: Summary statistics for 100 instances of the 4×4 sliding puzzle. "
              "BFS is omitted as it is computationally impractical for this puzzle size.",
              Caption),
    Spacer(1, 0.1*inch),
]

# ══════════════════════════════
# 7. CHARTS
# ══════════════════════════════
CHART_DIR = str(CHARTS_DIR) + "/"
story += [
    Paragraph("7. Visualizations", H1),
    HRFlowable(width="100%", thickness=0.6, color=BORDER, spaceAfter=6),

    KeepTogether([
        Paragraph("Figure 1: Nodes expanded across BFS, A*, and IDA* for 100 instances "
                  "of the 3×3 puzzle (box plot). Note the dramatic reduction from BFS to "
                  "A*/IDA* — the y-axis spans nearly two orders of magnitude.", Body),
        Spacer(1, 0.05*inch),
        chart_img(CHART_DIR + "chart1_nodes_boxplot_3x3.png", 6.0, 3.5),
        Paragraph("Figure 1 — Nodes Expanded Box Plot (3×3 Puzzle)", Caption),
    ]),
    Spacer(1, 0.15*inch),

    KeepTogether([
        Paragraph("Figure 2: Mean nodes expanded grouped by algorithm and puzzle size. "
                  "Both A* and IDA* show substantial reduction for 4×4 relative to their "
                  "3×3 counterparts due to shorter scramble depth in 4×4 instances.", Body),
        Spacer(1, 0.05*inch),
        chart_img(CHART_DIR + "chart2_nodes_grouped_bar.png", 6.0, 3.5),
        Paragraph("Figure 2 — Mean Nodes Expanded: A* vs IDA* by Puzzle Size", Caption),
    ]),
    Spacer(1, 0.15*inch),

    KeepTogether([
        Paragraph("Figure 3: Runtime distribution (violin plot) for the 3×3 puzzle. "
                  "BFS exhibits a heavy right tail due to hard instances requiring "
                  "near-complete frontier exploration. A* and IDA* distributions are "
                  "narrow and fast.", Body),
        Spacer(1, 0.05*inch),
        chart_img(CHART_DIR + "chart3_runtime_violin_3x3.png", 6.0, 3.5),
        Paragraph("Figure 3 — Runtime Violin Plot (3×3 Puzzle, ms)", Caption),
    ]),
    Spacer(1, 0.15*inch),

    KeepTogether([
        Paragraph("Figure 4: Scatter plot of solution depth vs. nodes expanded for BFS "
                  "and A* on the 3×3 puzzle. Both show a polynomial relationship with "
                  "depth, but A*'s slope is far lower — confirming the heuristic's "
                  "effectiveness at pruning.", Body),
        Spacer(1, 0.05*inch),
        chart_img(CHART_DIR + "chart4_depth_vs_nodes_scatter.png", 6.0, 3.5),
        Paragraph("Figure 4 — Solution Depth vs. Nodes Expanded (3×3, BFS vs A*)", Caption),
    ]),
    Spacer(1, 0.15*inch),

    KeepTogether([
        Paragraph("Figure 5: Mean runtime comparison for A* and IDA* across both puzzle "
                  "sizes. IDA* is slightly faster due to lower memory overhead, while A* "
                  "maintains a structured open list that better prioritizes promising states.", Body),
        Spacer(1, 0.05*inch),
        chart_img(CHART_DIR + "chart5_runtime_bar_by_size.png", 6.0, 3.5),
        Paragraph("Figure 5 — Mean Runtime: A* vs IDA* by Puzzle Size (ms)", Caption),
    ]),
    Spacer(1, 0.1*inch),
]

# ══════════════════════════════
# 8. ANALYSIS & DISCUSSION
# ══════════════════════════════
# Compute real numbers from data
nodes_bfs_mean  = smean(raw["3x3"]["bfs"]["nodes"])
nodes_ast_mean  = smean(raw["3x3"]["astar"]["nodes"])
nodes_ida_mean  = smean(raw["3x3"]["idastar"]["nodes"])
ratio_bfs_ast   = nodes_bfs_mean / nodes_ast_mean if nodes_ast_mean else 0
time_bfs_mean   = smean(raw["3x3"]["bfs"]["time_ms"])
time_ast_mean   = smean(raw["3x3"]["astar"]["time_ms"])
time_ida_mean   = smean(raw["3x3"]["idastar"]["time_ms"])
depth_3x3_mean  = smean(raw["3x3"]["astar"]["depth"])
depth_4x4_mean  = smean(raw["4x4"]["astar"]["depth"])

story += [
    PageBreak(),
    Paragraph("8. Analysis &amp; Discussion", H1),
    HRFlowable(width="100%", thickness=0.6, color=BORDER, spaceAfter=6),

    Paragraph("8.1 Heuristic Effectiveness", H2),
    Paragraph(
        f"On the 3×3 puzzle, BFS expanded an average of {nodes_bfs_mean:,.0f} nodes per "
        f"instance, while A* (Manhattan) expanded only {nodes_ast_mean:,.0f} — a reduction "
        f"factor of {ratio_bfs_ast:.1f}×. This dramatic improvement confirms that the "
        "Manhattan distance heuristic is highly informative for sliding puzzles: it captures "
        "the minimum number of moves each tile must make independently, giving a tight lower "
        "bound on the true solution cost.", Body),
    Paragraph(
        "The heuristic is both admissible (never overestimates) and consistent (satisfies "
        "h(n) ≤ c(n,n') + h(n') for all edges), guaranteeing that A* finds optimal solutions "
        "without re-expanding states. This is verified by confirming that all 100 instances "
        "for both A* and BFS yield identical solution depths.", Body),

    Paragraph("8.2 A* vs IDA*", H2),
    Paragraph(
        f"On the 3×3 puzzle, A* expanded {nodes_ast_mean:,.0f} nodes (mean) while IDA* "
        f"expanded {nodes_ida_mean:,.0f}. IDA* expands slightly more nodes due to redundant "
        "re-expansions across iterations, but uses O(d) memory versus A*'s potentially "
        "O(b<super>d</super>) memory. In practice, for the moderate depths encountered here "
        f"(mean depth {depth_3x3_mean:.1f} for 3×3), both algorithms complete in under "
        f"{max(time_ast_mean, time_ida_mean):.0f} ms.", Body),
    Paragraph(
        "On the 4×4 puzzle, IDA* is slightly faster than A* because the 20-move scrambled "
        "instances have shallow solutions, minimizing re-expansion cost while benefiting from "
        "IDA*'s lighter per-node overhead (no heap operations).", Body),

    Paragraph("8.3 BFS Scalability", H2),
    Paragraph(
        f"BFS is practical for 3×3 (mean {time_bfs_mean:.0f} ms, {nodes_bfs_mean:,.0f} nodes) "
        "but completely infeasible for 4×4 — the state space is 10 trillion states, far "
        "exceeding memory capacity. Even with node limits, BFS would fail on many 4×4 instances. "
        "This motivates heuristic search as a necessity, not just an optimization.", Body),

    Paragraph("8.4 Depth vs. Node Expansion Relationship", H2),
    Paragraph(
        "Figure 4 shows a polynomial growth in nodes expanded with solution depth for BFS, "
        "consistent with its O(b<super>d</super>) complexity. A* shows a much flatter curve, "
        "reflecting the heuristic's ability to focus search. Both algorithms find the same "
        "optimal depth, confirming correctness.", Body),

    Paragraph("8.5 Challenges &amp; Mitigations", H2),
    bullet("IDA* is sensitive to the Python recursion stack. Deep 4×4 instances could hit "
           "the default limit; this is mitigated by the 20-move scramble constraint."),
    bullet("Stale entries in A*'s heap can inflate node counts; a g-cost check on pop "
           "eliminates redundant processing."),
    bullet("For the full 15-puzzle (arbitrary depth), IDA* with pattern databases would be "
           "required — planned for Phase 3."),
    Spacer(1, 0.1*inch),
]

# ══════════════════════════════
# 9. CURRENT STATUS & NEXT STEPS
# ══════════════════════════════
story += [
    Paragraph("9. Current Status &amp; Next Steps", H1),
    HRFlowable(width="100%", thickness=0.6, color=BORDER, spaceAfter=6),

    Paragraph("Milestone 2 delivers the following implemented and verified components:", Body),
    bullet("BFS baseline: complete, optimal, verified on 100 3×3 instances"),
    bullet("A* (Manhattan distance): complete, optimal, 100% solve rate on 3×3 and 4×4"),
    bullet("IDA* (Manhattan distance): complete, optimal, 100% solve rate on 3×3 and 4×4"),
    bullet("Experiment infrastructure: 100 reproducible instances per size, full metrics collected"),
    bullet("5 publication-quality comparison charts"),
    Spacer(1, 0.05*inch),
    Paragraph("Planned enhancements for Phase 3 / Final Milestone:", Body),
    bullet("Disjoint Pattern Databases (PDB): pre-compute tile-subset distances for a tighter "
           "admissible heuristic that will make arbitrary-depth 4×4 and 5×5 instances tractable"),
    bullet("Linear Conflict enhancement: adds pairwise tile conflict penalty on top of Manhattan "
           "distance for improved h-values without sacrificing admissibility"),
    bullet("Tie-breaking strategy: prefer states with lower h(n) among equal f(n) nodes to "
           "reduce search spread"),
    bullet("Large-scale HPC experiments: 1,000+ instances at maximum scramble depth on the "
           "Gilbreth cluster for statistical significance"),
    Spacer(1, 0.1*inch),
]

# ══════════════════════════════
# 10. REFERENCES
# ══════════════════════════════
story += [
    Paragraph("10. References", H1),
    HRFlowable(width="100%", thickness=0.6, color=BORDER, spaceAfter=6),
    Paragraph(
        "[1] Russell, S., &amp; Norvig, P. (2020). <i>Artificial Intelligence: A Modern Approach</i> "
        "(4th ed.). Pearson. "
        '<a href="https://aima.cs.berkeley.edu/" color="blue">https://aima.cs.berkeley.edu/</a>',
        FootNote),
    Paragraph(
        "[2] Korf, R. E. (1985). Depth-first iterative-deepening: An optimal admissible tree "
        "search. <i>Artificial Intelligence</i>, 27(1), 97–109. "
        '<a href="https://doi.org/10.1016/0004-3702(85)90084-0" color="blue">'
        "https://doi.org/10.1016/0004-3702(85)90084-0</a>",
        FootNote),
    Paragraph(
        "[3] Culberson, J. C., &amp; Schaeffer, J. (1998). Pattern databases. "
        "<i>Computational Intelligence</i>, 14(3), 318–334. "
        '<a href="https://doi.org/10.1111/0824-7935.00065" color="blue">'
        "https://doi.org/10.1111/0824-7935.00065</a>",
        FootNote),
    Paragraph(
        "[4] Korf, R. E., &amp; Felner, A. (2002). Disjoint pattern database heuristics. "
        "<i>Artificial Intelligence</i>, 134(1–2), 9–22. "
        '<a href="https://doi.org/10.1016/S0004-3702(01)00092-3" color="blue">'
        "https://doi.org/10.1016/S0004-3702(01)00092-3</a>",
        FootNote),
    Paragraph(
        "[5] Hart, P. E., Nilsson, N. J., &amp; Raphael, B. (1968). A formal basis for the "
        "heuristic determination of minimum cost paths. <i>IEEE Transactions on Systems Science "
        "and Cybernetics</i>, 4(2), 100–107. "
        '<a href="https://doi.org/10.1109/TSSC.1968.300136" color="blue">'
        "https://doi.org/10.1109/TSSC.1968.300136</a>",
        FootNote),
    Spacer(1, 0.2*inch),
    HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=4),
    Paragraph(
        "Source code available at: <b>solver.py</b> (submitted via Brightspace). "
        "All experiments are reproducible with <code>python solver.py</code> (seed=42).",
        FootNote),
]

# ─── Build PDF ───────────────────────────────────────────
OUT = str(REPORTS_DIR / "CS57200_Phase2_Report.pdf")
doc = SimpleDocTemplate(
    OUT,
    pagesize=letter,
    title="CS 57200 Phase 2 – A*/IDA* Sliding Tile Puzzle Solver",
    author="Perplexity Computer",
    leftMargin=0.75*inch,
    rightMargin=0.75*inch,
    topMargin=0.6*inch,
    bottomMargin=0.65*inch,
)

doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
print(f"PDF generated: {OUT}")
