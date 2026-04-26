# Changelog

All notable changes are listed in reverse chronological order.

## Phase 3 — Final deliverable (April 2026)

### Added
- `heuristics.py`: three admissible heuristics — Manhattan, Manhattan + Linear Conflict, Disjoint additive PDB (4-4-4-3 partition).
- `solver.py` rewrite: BFS, A*, and IDA* now accept a heuristic callable, enabling trivial ablation.
- `ablation.py`: Phase 3 experiment runner across scramble depths 20 / 30 / 50.
- `ablation_charts.py`: six rendered figures including the architecture diagram, with bootstrap 95% CIs (1000 resamples).
- `make_final_report.py`: ReportLab generator producing the 11-page final report.
- `build_slides.js`: PptxGenJS generator producing the 13-slide presentation deck.
- `CS57200_Final_Report.pdf`, `CS57200_Final_Slides.pptx`, `CS57200_Final_Slides.pdf`.
- `CHANGELOG.md` (this file).

### Fixed
- IDA* now reports the actual solution depth instead of a stale `len(path) - 1`.

### Changed
- README rewritten to describe the final deliverable.
- Charts now report bootstrap mean with 95% confidence intervals on every figure that aggregates results.

## Phase 2 — Milestone 2 (March 2026)

### Added
- BFS / A* / IDA* solvers with Manhattan distance.
- 3×3 and 4×4 scramble-depth scaling experiments.
- `CS57200_Phase2_Report.pdf`, `CS57200_DepthScaling_Extension.pdf`, `CS57200_4x4_DepthScaling.pdf`.
- Continuous integration on push (lint + smoke test).

## Milestone 1 (February 2026)

### Added
- Project proposal and initial repository skeleton.
