# CS 57200 – Milestone 2 Submission
**Heuristic A* Search for Large Sliding Puzzles Using Advanced Heuristics**

- **Course:** CS 57200: Heuristic Problem Solving, Purdue University
- **Track:** B — Search & Optimization
- **Student:** Akwasi (akwasi@usiu.ac.ke)
- **Due:** April 9, 2026 via Brightspace

---

## Submission Contents

### Reports (PDF)
| File | Description |
|------|-------------|
| `CS57200_Phase2_Report.pdf` | **Main Milestone 2 report** — BFS vs A* vs IDA* on 3×3 and 4×4 puzzles, 100 instances each, 5 comparison charts, results tables, and analysis (10 pages) |
| `CS57200_DepthScaling_Extension.pdf` | **Extension A** — 3×3 scramble-depth sweep (depths 10/20/30/50/75), showing depth saturation at ~21 moves and 54–56× heuristic gain over BFS (6 pages) |
| `CS57200_4x4_DepthScaling.pdf` | **Extension B** — 4×4 scramble-depth sweep (depths 10/20/30/50), showing A*/IDA* crossover at solution depth ~22–25 and absence of depth saturation (7 pages) |

### Source Code (Python)
| File | Description |
|------|-------------|
| `solver.py` | **Core module** — BFS, A*, and IDA* solvers; puzzle instance generator; Phase 2 experiment runner (100 instances per size, seed=42) |
| `make_charts.py` | Generates 5 Phase 2 comparison charts (nodes, runtime, depth scatter) |
| `make_report.py` | Generates `CS57200_Phase2_Report.pdf` from results data and charts |
| `depth_scaling.py` | 3×3 depth-scaling experiment runner — scrambles 10/20/30/50/75, 50 instances each, seed=99 |
| `depth_scaling_charts.py` | Generates 5 charts for the 3×3 depth-scaling extension |
| `make_depth_report.py` | Generates `CS57200_DepthScaling_Extension.pdf` |
| `depth_scaling_4x4.py` | 4×4 depth-scaling experiment runner — scrambles 10/20/30/50, 50 instances each, seed=77; saves results incrementally |
| `depth_scaling_4x4_charts.py` | Generates 6 charts for the 4×4 depth-scaling extension |
| `make_4x4_depth_report.py` | Generates `CS57200_4x4_DepthScaling.pdf` |

---

## Reproducing the Results

### Requirements
```
Python 3.9+
pip install reportlab matplotlib numpy
```

### Run Order
```bash
# Phase 2 main experiment
python solver.py                    # → raw_results.json, summary.json
python make_charts.py               # → charts/chart1–5.png
python make_report.py               # → CS57200_Phase2_Report.pdf

# 3×3 depth-scaling extension
python depth_scaling.py             # → depth_scaling_results.json
python depth_scaling_charts.py      # → charts/chartA–E.png
python make_depth_report.py         # → CS57200_DepthScaling_Extension.pdf

# 4×4 depth-scaling extension
python depth_scaling_4x4.py         # → depth_scaling_4x4_results.json
                                    #   (scramble-75 will time out — expected;
                                    #    results for depths 10/20/30/50 save incrementally)
python depth_scaling_4x4_charts.py  # → charts4x4/chart1–6.png
python make_4x4_depth_report.py     # → CS57200_4x4_DepthScaling.pdf
```

---

## Design Summary

### State Representation
- Immutable Python `tuple` of length n² (n=3 or n=4)
- Tile `0` represents the blank; goal state = `(1, 2, …, n²-1, 0)`

### Instance Generation
- Random walks from the goal state (parent state excluded to avoid back-tracking)
- Guarantees solvability by construction; reproducible via fixed seeds

### Algorithms
| Algorithm | Strategy | Heuristic |
|-----------|----------|-----------|
| BFS | FIFO + visited dict | None |
| A* | Lazy-deletion heap + g-cost map | Manhattan distance |
| IDA* | Iterative deepening DFS on f-bound | Manhattan distance |

### Reproducibility Seeds
| Experiment | Seed |
|-----------|------|
| Phase 2 (100 instances per size) | 42 |
| 3×3 depth scaling (50 instances per tier) | 99 |
| 4×4 depth scaling (50 instances per tier) | 77 |

---

## Key Findings

- **A* vs BFS (3×3):** A* expands 47× fewer nodes on average; 16× faster
- **Depth saturation (3×3):** Solution depth plateaus at ~21 moves past scramble-30; heuristic efficiency gain stabilizes at 54–56×
- **4×4 crossover:** IDA* outperforms A* at shallow depths (≤~22 moves); A* dominates at depth 25+
- **4×4 saturation:** No saturation observed through scramble-50 (solution depths still growing at 34 moves)
- **IDA* tractability:** Intractable on 4×4 at scramble-75 with Manhattan-distance heuristic alone
