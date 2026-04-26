# CS 57200 — Final Project Submission
**Heuristic A* Search for Large Sliding Puzzles Using Advanced Heuristics**

- **Course:** CS 57200: Heuristic Problem Solving, Purdue University, Spring 2026
- **Track:** B — Search & Optimization
- **Student:** Anthony Kwasi (akwasi@usiu.ac.ke)

---

## Final Deliverables

### Top-level artefacts
| File | Description |
|------|-------------|
| `CS57200_Final_Report.pdf` | **Final integrated report** — 11 pages. Cover, abstract, related work (12 references), system design, methodology, results with bootstrap 95% CIs, analysis, conclusion, future work, reproducibility appendix. |
| `CS57200_Final_Slides.pptx` | **15-minute presentation deck** — 13 slides covering motivation, background, architecture, three heuristics, results, analysis, takeaways. |

### Earlier milestone PDFs (kept for context)
| File | Description |
|------|-------------|
| `CS57200_Phase2_Report.pdf` | Milestone 2 main report — BFS vs A* vs IDA* with Manhattan distance, 100 instances per size. |
| `CS57200_DepthScaling_Extension.pdf` | 3×3 scramble-depth sweep extension. |
| `CS57200_4x4_DepthScaling.pdf` | 4×4 scramble-depth sweep extension. |

### Phase 3 ablation outputs
| File | Description |
|------|-------------|
| `ablation_4x4_d20.json`, `ablation_4x4_d30.json`, `ablation_4x4_d50.json` | Per-instance Phase 3 results — Manhattan vs Linear Conflict vs Disjoint PDB at three scramble depths. |
| `charts_phase3/chart1_*.png` … `chart6_architecture.png` | Six rendered figures including the system architecture diagram. |

---

## Source Code

### Phase 3 (final) — heuristic ablation
| File | Description |
|------|-------------|
| `heuristics.py` | **Three admissible heuristics** — Manhattan distance, Manhattan + Linear Conflict (Hansson, Mayer & Yung 1992), and a Disjoint additive Pattern Database (Korf & Felner 2002) with a 4-4-4-3 partition built via 0-1 BFS in projected space. |
| `solver.py` | **Pluggable BFS / A\* / IDA\* solvers.** Heuristic is passed as a callable so the same code path is reused across all heuristics. Lazy-deletion heap for A\*; iterative-deepening with f-thresholds for IDA\*; parent-state pruning. |
| `ablation.py` | Phase 3 experiment runner — Manhattan vs Linear Conflict vs Disjoint PDB at scramble depths 20, 30, 50 (seed = 1234). |
| `ablation_charts.py` | Generates six Phase 3 figures with bootstrap 95% confidence intervals (1000 resamples), including the architecture diagram. |
| `make_final_report.py` | ReportLab generator that produces `CS57200_Final_Report.pdf`. |
| `build_slides.js` | PptxGenJS generator that produces `CS57200_Final_Slides.pptx`. |

### Phase 2 (legacy)
| File | Description |
|------|-------------|
| `make_charts.py`, `make_report.py` | Phase 2 chart and PDF generators. |
| `depth_scaling.py`, `depth_scaling_charts.py`, `make_depth_report.py` | 3×3 depth-scaling extension. |
| `depth_scaling_4x4.py`, `depth_scaling_4x4_charts.py`, `make_4x4_depth_report.py` | 4×4 depth-scaling extension. |

---

## Reproducing the Results

### Requirements
```
Python 3.9+
pip install -r requirements.txt
```
Dependencies: `reportlab`, `matplotlib`, `numpy`.

### Run order
```bash
# Phase 2 (Manhattan baseline)
python solver.py                  # raw_results.json, summary.json
python make_charts.py             # charts/chart1-5.png
python make_report.py             # CS57200_Phase2_Report.pdf

# 3x3 / 4x4 depth-scaling extensions
python depth_scaling.py
python depth_scaling_charts.py
python make_depth_report.py
python depth_scaling_4x4.py
python depth_scaling_4x4_charts.py
python make_4x4_depth_report.py

# Phase 3 (heuristic ablation - the final deliverable)
python ablation.py --n 4 --scramble 20 --instances 50 --out ablation_4x4_d20.json
python ablation.py --n 4 --scramble 30 --instances 50 --out ablation_4x4_d30.json
python ablation.py --n 4 --scramble 50 --instances 30 --out ablation_4x4_d50.json
python ablation_charts.py         # charts_phase3/chart1-6.png
python make_final_report.py       # CS57200_Final_Report.pdf
```

---

## Design Summary

### State Representation
- Immutable Python `tuple` of length n² (n = 3 or n = 4); tile `0` is the blank.
- Goal state: `(1, 2, …, n²−1, 0)`.

### Algorithms
| Algorithm | Strategy | Memory |
|-----------|----------|--------|
| BFS | Deque + predecessor map | O(b^d) |
| A* | Binary heap on (f, g, state); lazy deletion | O(b^d) |
| IDA* | Iterative-deepening DFS bounded by f-threshold; parent-state pruning | O(d) |

All three accept a heuristic callable `h(state) -> int`.

### Heuristic Stack
| Heuristic | Source | Notes |
|-----------|--------|-------|
| Manhattan distance | Russell & Norvig 2021 | O(n²) per call. Baseline. |
| Manhattan + Linear Conflict | Hansson, Mayer & Yung 1992 | +2 per row/column conflict, greedy max-conflict removal. |
| Disjoint Pattern Database | Korf & Felner 2002 | 4-4-4-3 partition. 0-1 BFS in projected space (group moves cost 1, others cost 0). 1.6 M entries; ~4 s build. |

### Reproducibility Seeds
| Experiment | Seed | Instances |
|-----------|------|-----------|
| Phase 2 main | 42 | 100 per size |
| 3×3 depth sweep | 99 | 50 per tier |
| 4×4 depth sweep | 77 | 50 per tier |
| Phase 3 ablation (final) | 1234 | 50 / 50 / 30 at d = 20 / 30 / 50 |

---

## Headline Results (Phase 3 ablation)

A\* on the 15-puzzle, mean nodes expanded across random instances; bootstrap 95% CIs in brackets.

| Depth | Manhattan | Linear Conflict | Disjoint PDB | PDB speedup |
|------:|----------:|----------------:|-------------:|------------:|
|  20 |   268 [203, 343] |   182 [141, 229] |   100 [72, 130] | **2.7×** |
|  30 | 5,896 [3,758, 8,425] | 2,328 [1,528, 3,263] | 1,012 [634, 1,467] | **5.8×** |
|  50 | 206,058 [80,300, 348,433] | 58,840 [21,729, 101,422] | 13,600 [5,980, 22,300] | **15.2×** |

- **Wall-clock speedup** for PDB at d = 50: **9.7×** over Manhattan.
- **Optimality preserved:** solution depths matched across all heuristics for every instance.
- **Linear Conflict** delivers a steady **1.5–3.5×** node-expansion speedup with no precomputation cost.

---

## Key Findings

- **A\* vs BFS (3×3):** A\* expands ~47× fewer nodes; 16× faster.
- **Depth saturation (3×3):** Solution depth plateaus at ~21 moves; heuristic gain stabilises at 54–56×.
- **4×4 crossover:** IDA\* outperforms A\* at shallow depths (≤ ~22 moves); A\* dominates beyond depth 25.
- **PDB headline:** 15.2× node-expansion speedup at d = 50 with strict optimality preserved.
- **PDB build cost:** Pure-Python 4-4-4-3 build completes in under 4 seconds; canonical 5-5-5 partition exposed but not pre-built (multi-hour Python build).

---

## Repository
[github.com/AnSikwa/Heuristics-Project_Anthony-Kwasi](https://github.com/AnSikwa/Heuristics-Project_Anthony-Kwasi)
