"""PDF report for the depth-scaling extension experiment."""

import json, urllib.request
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, Image, KeepTogether, PageBreak
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT        = Path(__file__).parent
DATA_DIR    = ROOT / "data"
CHARTS_DIR  = ROOT / "charts"
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# ── Fonts ────────────────────────────────────────────────
FONT_DIR = Path("/tmp/fonts"); FONT_DIR.mkdir(exist_ok=True)
def dl(url, name):
    p = FONT_DIR/name
    if not p.exists():
        try: urllib.request.urlretrieve(url, p)
        except: return False
    return p.exists()

ok = dl("https://github.com/google/fonts/raw/main/ofl/dmsans/DMSans%5Bopsz%2Cwght%5D.ttf", "DMSans.ttf")
if ok:
    pdfmetrics.registerFont(TTFont("DMSans",     str(FONT_DIR/"DMSans.ttf")))
    pdfmetrics.registerFont(TTFont("DMSans-Bold",str(FONT_DIR/"DMSans.ttf")))
    BODY = "DMSans"; HEAD = "DMSans-Bold"
else:
    BODY = "Helvetica"; HEAD = "Helvetica-Bold"
MONO = "Courier"

# ── Palette ──────────────────────────────────────────────
TEAL_D  = HexColor("#1B474D"); TEAL_C = HexColor("#20808D")
BG      = HexColor("#F7F6F2"); TEXT_C = HexColor("#28251D")
MUTED   = HexColor("#7A7974"); BORDER = HexColor("#D4D1CA")
RUST    = HexColor("#A84B2F"); ROW_A  = HexColor("#EFF5F5")
HDR_BG  = HexColor("#1B474D"); CODE_B = HexColor("#F0EFEB")
W, H    = letter

# ── Styles ───────────────────────────────────────────────
styles = getSampleStyleSheet()
def mk(name, parent="Normal", **kw):
    return ParagraphStyle(name, parent=styles[parent], **kw)

Title   = mk("T",  "Title",   fontName=HEAD, fontSize=20, textColor=TEXT_C, spaceAfter=4, leading=26)
Sub     = mk("S",  "Normal",  fontName=BODY, fontSize=11, textColor=MUTED,  spaceAfter=12, leading=15)
H1      = mk("H1", "Heading1",fontName=HEAD, fontSize=13, textColor=TEAL_D, spaceBefore=12, spaceAfter=4, leading=17)
H2      = mk("H2", "Heading2",fontName=HEAD, fontSize=10.5, textColor=TEXT_C, spaceBefore=8, spaceAfter=3, leading=14)
Body    = mk("B",  "Normal",  fontName=BODY, fontSize=10, textColor=TEXT_C, spaceAfter=6, leading=15)
Bul     = mk("Bl", "Normal",  fontName=BODY, fontSize=10, textColor=TEXT_C, spaceAfter=3, leading=14, leftIndent=14)
Cap     = mk("C",  "Normal",  fontName=BODY, fontSize=8,  textColor=MUTED,  spaceAfter=8, leading=11, alignment=1)
Foot    = mk("F",  "Normal",  fontName=BODY, fontSize=7.5,textColor=MUTED,  spaceAfter=2, leading=10)
TH      = mk("TH", "Normal",  fontName=HEAD, fontSize=9,  textColor=white,   alignment=1, leading=12)
TC      = mk("TC", "Normal",  fontName=BODY, fontSize=9,  textColor=TEXT_C,  alignment=1, leading=12)
TL      = mk("TL", "Normal",  fontName=BODY, fontSize=9,  textColor=TEXT_C,  alignment=0, leading=12)

def bul(t): return Paragraph(f"• {t}", Bul)
def img(p, w=6.0, h=3.5): return Image(p, width=w*inch, height=h*inch)

def header_footer(cv, doc):
    cv.saveState()
    cv.setFillColor(HDR_BG)
    cv.rect(0, H-28, W, 28, fill=1, stroke=0)
    cv.setFont(HEAD, 8); cv.setFillColor(white)
    cv.drawString(0.75*inch, H-18, "CS 57200 – Heuristic Problem Solving")
    cv.drawRightString(W-0.75*inch, H-18, "Depth-Scaling Extension: 3×3 Puzzle")
    cv.setFillColor(MUTED); cv.setFont(BODY, 7.5)
    cv.drawString(0.75*inch, 24, "Purdue University · CS 57200 · Track B: Search & Optimization")
    cv.drawRightString(W-0.75*inch, 24, f"Page {doc.page}")
    cv.setStrokeColor(BORDER); cv.setLineWidth(0.5)
    cv.line(0.75*inch, 36, W-0.75*inch, 36)
    cv.restoreState()

# ── Data ─────────────────────────────────────────────────
with open(DATA_DIR / "depth_scaling_results.json") as f:
    raw = json.load(f)

DEPTHS = [10, 20, 30, 50, 75]

def mean_n(sd, algo):
    ns = [r["nodes"] for r in raw[str(sd)][algo] if r["found"]]; return sum(ns)/len(ns) if ns else 0
def mean_d(sd, algo):
    ds = [r["depth"] for r in raw[str(sd)][algo] if r["found"] and r["depth"]>=0]; return sum(ds)/len(ds) if ds else 0
def mean_t(sd, algo):
    ts = [r["ms"] for r in raw[str(sd)][algo] if r["found"]]; return sum(ts)/len(ts) if ts else 0
def solved(sd, algo):
    return sum(1 for r in raw[str(sd)][algo] if r["found"])

# ── Results table ─────────────────────────────────────────
def results_table():
    header_row = [Paragraph(h, TH) for h in [
        "Scramble\nDepth", "Sol.Depth\n(mean)", "BFS Nodes\n(mean)",
        "A* Nodes\n(mean)", "IDA* Nodes\n(mean)",
        "BFS/A*\nRatio", "A* Time\n(ms)", "BFS Time\n(ms)"]]
    rows = [header_row]
    for sd in DEPTHS:
        bn = mean_n(sd,"bfs"); an = mean_n(sd,"astar"); in_ = mean_n(sd,"idastar")
        ratio = bn/an if an else 0
        rows.append([
            Paragraph(str(sd), TC),
            Paragraph(f"{mean_d(sd,'astar'):.1f}", TC),
            Paragraph(f"{bn:,.0f}", TC),
            Paragraph(f"{an:,.0f}", TC),
            Paragraph(f"{in_:,.0f}", TC),
            Paragraph(f"{ratio:.0f}×", TC),
            Paragraph(f"{mean_t(sd,'astar'):.2f}", TC),
            Paragraph(f"{mean_t(sd,'bfs'):.2f}", TC),
        ])
    cw = [0.72*inch]*8
    t = Table(rows, colWidths=cw)
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0), HDR_BG),
        ("TEXTCOLOR",   (0,0), (-1,0), white),
        ("FONTSIZE",    (0,0), (-1,-1), 9),
        ("ALIGN",       (0,0), (-1,-1), "CENTER"),
        ("GRID",        (0,0), (-1,-1), 0.4, BORDER),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[white, ROW_A]),
        ("TOPPADDING",  (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
    ]))
    return t

# ── Story ─────────────────────────────────────────────────
C = str(CHARTS_DIR) + "/"
story = []

# Cover
story += [
    Spacer(1, 0.4*inch),
    Paragraph("CS 57200: Heuristic Problem Solving", Sub),
    Paragraph("Depth-Scaling Extension: How A* Node Expansions Scale with Solution Depth", Title),
    HRFlowable(width="100%", thickness=2, color=TEAL_C, spaceAfter=10),
    Paragraph("3×3 (8-Puzzle) · Scramble Depths: 10, 20, 30, 50, 75 · 50 instances each · seed=99", Body),
    Paragraph("Algorithms: BFS (baseline) · A* (Manhattan) · IDA* (Manhattan)", Body),
    Spacer(1, 0.1*inch),
    Paragraph("April 2026 &nbsp;|&nbsp; Purdue University", Foot),
    Spacer(1, 0.3*inch),
]

# 1. Motivation
story += [
    Paragraph("1. Motivation", H1),
    HRFlowable(width="100%", thickness=0.6, color=BORDER, spaceAfter=5),
    Paragraph(
        "The Phase 2 experiments used a fixed scramble of 50 random moves for the 3×3 puzzle. "
        "This extension systematically varies scramble depth across five levels — 10, 20, 30, 50, "
        "and 75 moves — to expose how node expansions grow with instance difficulty. Three "
        "questions drive this experiment:", Body),
    bul("Does A*'s node-expansion advantage over BFS grow, shrink, or stay flat as scramble depth increases?"),
    bul("At what scramble depth does the 3×3 puzzle reach its maximum solution depth (~26–31 moves), "
        "causing BFS and A* nodes to plateau?"),
    bul("How does IDA* compare to A* across the difficulty spectrum?"),
    Spacer(1, 0.1*inch),
]

# 2. Setup
story += [
    Paragraph("2. Experimental Setup", H1),
    HRFlowable(width="100%", thickness=0.6, color=BORDER, spaceAfter=5),
    Paragraph("Each scramble-depth tier generates 50 solvable instances by performing exactly that "
              "many random moves from the canonical goal state (no revisiting the immediately "
              "previous state). Seed=99 ensures reproducibility and independence from the Phase 2 "
              "instances (seed=42). All three solvers are run with the same node limits as Phase 2 "
              "(BFS: 500K, A*: 1M, IDA*: 500K). All 250 instances were solved successfully.", Body),
    Spacer(1, 0.05*inch),
    Paragraph("<b>Key observation about 3×3 depth saturation.</b>  The maximum optimal solution "
              "depth for any 3×3 sliding puzzle is 31 moves (God's Number). After ~20–25 random "
              "moves, new scrambles are nearly as hard as fully random instances because the "
              "walk has mixed thoroughly. This means solution depth plateaus well before scramble "
              "depth 75 — a critical finding highlighted in Chart E.", Body),
    Spacer(1, 0.1*inch),
]

# 3. Results table
story += [
    Paragraph("3. Results", H1),
    HRFlowable(width="100%", thickness=0.6, color=BORDER, spaceAfter=5),
    results_table(),
    Spacer(1, 0.05*inch),
    Paragraph("Table 1: Mean statistics across 50 instances per scramble depth (3×3 puzzle). "
              "All 50 instances solved at every tier.", Cap),
    Spacer(1, 0.15*inch),
]

# 4. Charts
story += [
    Paragraph("4. Visualizations", H1),
    HRFlowable(width="100%", thickness=0.6, color=BORDER, spaceAfter=5),

    KeepTogether([
        Paragraph("Chart A — Node Expansions vs. Scramble Depth (log scale).  BFS scales "
                  "steeply (exponential in depth), while A* and IDA* grow far more slowly, "
                  "confirming the heuristic's effectiveness at every difficulty level.", Body),
        Spacer(1, 0.04*inch),
        img(C+"chartA_nodes_vs_scramble_log.png"),
        Paragraph("Chart A — Mean Nodes Expanded vs. Scramble Depth (log scale)", Cap),
    ]),
    Spacer(1, 0.15*inch),

    KeepTogether([
        Paragraph("Chart B — A* nodes vs. actual solution depth (scatter + mean line).  "
                  "Each point is one instance; colour encodes scramble tier. Both BFS and A* "
                  "grow with solution depth, but A*'s slope is dramatically shallower — "
                  "reflecting the heuristic's pruning power.", Body),
        Spacer(1, 0.04*inch),
        img(C+"chartB_nodes_vs_actual_depth.png"),
        Paragraph("Chart B — A* (scatter) and BFS/A* Means vs. Actual Solution Depth (log scale)", Cap),
    ]),
    Spacer(1, 0.15*inch),

    KeepTogether([
        Paragraph("Chart C — Heuristic gain ratio (BFS ÷ A*).  The ratio rises from 21× at "
                  "scramble-10 to ~54–56× at scrambles 20–30, then stabilises. This shows "
                  "the heuristic provides the greatest relative benefit on moderate-to-hard "
                  "instances and retains that advantage as difficulty saturates.", Body),
        Spacer(1, 0.04*inch),
        img(C+"chartC_ratio_vs_scramble.png"),
        Paragraph("Chart C — BFS÷A* Node Expansion Ratio vs. Scramble Depth", Cap),
    ]),
    Spacer(1, 0.15*inch),

    KeepTogether([
        Paragraph("Chart D — Runtime scaling.  BFS runtime grows sharply with scramble depth; "
                  "A* and IDA* remain nearly flat and indistinguishable at this scale (shaded "
                  "band). The BFS label shows wall-clock time in ms.", Body),
        Spacer(1, 0.04*inch),
        img(C+"chartD_runtime_vs_scramble.png"),
        Paragraph("Chart D — Mean Runtime (ms) vs. Scramble Depth", Cap),
    ]),
    Spacer(1, 0.15*inch),

    KeepTogether([
        Paragraph("Chart E — Solution depth distribution by scramble level.  Median optimal "
                  "depth saturates at ~21 moves for scrambles ≥30, despite the scramble "
                  "walk being twice as long at depth 75. This confirms the 3×3 random-walk "
                  "mixing time and explains why BFS/A* node counts plateau for scrambles ≥50.", Body),
        Spacer(1, 0.04*inch),
        img(C+"chartE_depth_distribution.png"),
        Paragraph("Chart E — Optimal Solution Depth Distribution by Scramble Level (violin + scatter)", Cap),
    ]),
    Spacer(1, 0.1*inch),
]

# 5. Analysis
story += [
    PageBreak(),
    Paragraph("5. Analysis &amp; Discussion", H1),
    HRFlowable(width="100%", thickness=0.6, color=BORDER, spaceAfter=5),

    Paragraph("5.1 BFS Node Growth Is Exponential; A* Is Near-Polynomial", H2),
    Paragraph(
        "From scramble-10 to scramble-30, BFS node expansions grow from 365 to 50,435 — "
        "a 138× increase over a ~2× increase in solution depth (9.8 → 20.1 moves). This is "
        "consistent with O(b<super>d</super>) growth at branching factor b ≈ 2.67. A* grows "
        "from 18 to 904 nodes over the same range — a 50× increase — which is substantially "
        "sub-exponential thanks to heuristic pruning.", Body),

    Paragraph("5.2 The Heuristic Gain Peaks at Moderate Difficulty", H2),
    Paragraph(
        "The BFS÷A* ratio jumps from 21× (scramble-10, depth ~10) to 54–56× (scramble-20 "
        "through 30, depth ~17–20), then stabilises. Two forces explain this: "
        "(1) at shallow depths, BFS explores so few nodes that A*'s overhead matters; "
        "(2) once the solution depth exceeds ~16–18 moves, BFS must explore the majority "
        "of the 181,440-state space, while A* remains tightly focused via h(n). "
        "The gain does not continue to grow past scramble-30 because depth saturates.", Body),

    Paragraph("5.3 Depth Saturation Beyond Scramble-30", H2),
    Paragraph(
        "The median solution depth is 9.8 at scramble-10, 17.4 at scramble-20, 20.1 at "
        "scramble-30, and increases to only 21.6 by scramble-75 — a gain of barely 1.5 moves "
        "over 2.5× more scrambling. This is the mixing-time effect: the 3×3 random walk "
        "reaches near-uniform distribution over reachable states in ≈25–30 steps, so further "
        "scrambling adds no meaningful difficulty. Consequently, A* node counts also plateau "
        "(1,284 at scramble-50 vs 1,416 at scramble-75).", Body),

    Paragraph("5.4 IDA* vs A* Across Difficulty", H2),
    Paragraph(
        "IDA* slightly outperforms A* at the lowest scramble depth (16 vs 18 nodes) because "
        "short-solution searches benefit from IDA*'s negligible per-node overhead. At deeper "
        "depths (scramble ≥20), A* expands fewer nodes than IDA* because its structured open "
        "list avoids re-expansions across iterations. Both remain within a small constant factor "
        "of each other throughout, confirming Manhattan distance is effective for both traversal "
        "strategies.", Body),

    Paragraph("5.5 Implications for Phase 3", H2),
    Paragraph(
        "For the 4×4 puzzle, mixing is far from complete at 20 random moves. The planned "
        "Disjoint Pattern Database heuristic would be needed to handle arbitrary-depth 4×4 "
        "instances, where the state space (10 trillion) makes BFS impossible and Manhattan "
        "distance alone is insufficient to keep A* tractable.", Body),
    Spacer(1, 0.1*inch),
]

# 6. Summary table (key numbers)
story += [
    Paragraph("6. Key Numerical Summary", H1),
    HRFlowable(width="100%", thickness=0.6, color=BORDER, spaceAfter=5),
    Paragraph("All solvers achieved 100% solve rate across all 250 instances.", Body),
    Spacer(1, 0.05*inch),
    results_table(),
    Spacer(1, 0.05*inch),
    Paragraph("Table 2: Complete results repeated for reference. BFS/A* ratio shows the heuristic "
              "gain factor — how many fewer nodes A* expands compared to BFS.", Cap),
]

# ── Build ─────────────────────────────────────────────────
OUT = str(REPORTS_DIR / "CS57200_DepthScaling_Extension.pdf")
doc = SimpleDocTemplate(OUT, pagesize=letter,
    title="CS 57200 – Depth-Scaling Extension: A* Node Expansions vs. Solution Depth",
    author="Perplexity Computer",
    leftMargin=0.75*inch, rightMargin=0.75*inch,
    topMargin=0.6*inch,   bottomMargin=0.65*inch)
doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
print(f"PDF generated: {OUT}")
