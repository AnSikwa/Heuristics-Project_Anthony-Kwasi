# CS 57200 – Phase 2: Sliding Tile Puzzle Solver
**Purdue University · Track B: Search & Optimization**  
**Project:** Heuristic A\* Search for Large Sliding Puzzles Using Advanced Heuristics  
**Due:** April 9, 2026 via Brightspace

---

## Quick Start

### Prerequisites
- Python 3.10 or higher

### Install dependencies

```bash
pip install -r requirements.txt
```

> **Tip:** Use a virtual environment to keep dependencies isolated:
> ```bash
> python -m venv .venv
> source .venv/bin/activate   # Windows: .venv\Scripts\activate
> pip install -r requirements.txt
> ```

---

## Files

| File | Purpose |
|------|---------|
| `solver.py` | Core solvers (BFS, A\*, IDA\*) + Phase 2 experiment runner |
| `make_charts.py` | Phase 2 charts (5 charts → `charts/`) |
| `make_report.py` | Phase 2 PDF report generator |
| `depth_scaling.py` | 3×3 depth-scaling experiment (scrambles 10/20/30/50/75) |
| `depth_scaling_charts.py` | 3×3 depth-scaling charts (5 charts → `charts/`) |
| `make_depth_report.py` | 3×3 depth-scaling PDF report generator |
| `depth_scaling_4x4.py` | 4×4 depth-scaling experiment (scrambles 10/20/30/50) |
| `depth_scaling_4x4_charts.py` | 4×4 depth-scaling charts (6 charts → `charts4x4/`) |
| `make_4x4_depth_report.py` | 4×4 depth-scaling PDF report generator |

Output directories are created automatically when each script runs:

| Directory | Contents |
|-----------|----------|
| `data/` | JSON result files (`raw_results.json`, `summary.json`, etc.) |
| `charts/` | Phase 2 and 3×3 depth-scaling PNG charts |
| `charts4x4/` | 4×4 depth-scaling PNG charts |
| `reports/` | Generated PDF reports |

---

## Reproduction

### Step 1 – Run Phase 2 main experiment
Generates `data/raw_results.json` and `data/summary.json`.
```bash
python solver.py
```

### Step 2 – Generate Phase 2 charts
```bash
python make_charts.py
```

### Step 3 – Generate Phase 2 PDF report
```bash
python make_report.py
```

### Step 4 – Run 3×3 depth-scaling experiment
```bash
python depth_scaling.py
```

### Step 5 – Generate 3×3 depth-scaling charts and report
```bash
python depth_scaling_charts.py
python make_depth_report.py
```

### Step 6 – Run 4×4 depth-scaling experiment
```bash
python depth_scaling_4x4.py
```
> Note: scramble depth 75 will time out (expected — IDA* intractable at that depth with Manhattan-only heuristic). Results for depths 10/20/30/50 are saved incrementally.

### Step 7 – Generate 4×4 charts and report
```bash
python depth_scaling_4x4_charts.py
python make_4x4_depth_report.py
```

---

## Seeds
| Experiment | Seed |
|-----------|------|
| Phase 2 (100 instances per size) | 42 |
| 3×3 depth scaling (50 instances per tier) | 99 |
| 4×4 depth scaling (50 instances per tier) | 77 |

---

## Key Design Decisions

- **State:** immutable Python `tuple`, length n², tile `0` = blank, goal = `(1..n²-1, 0)`
- **Instance generation:** random moves from goal (never back to parent) — guarantees solvability by construction
- **BFS:** FIFO deque + visited dict — only run on 3×3
- **A\*:** lazy-deletion heap, g-cost hash map, parent dict for depth reconstruction
- **IDA\*:** DFS with iterative f-bound, parent pruning to avoid back-tracking, node counter for limit
- **4×4 IDA\* limits:** 500K (scramble-10/20), 1M (scramble-30/50) — instances exceeding limit logged as DNF

---

## Results Summary

### Phase 2 (100 instances, seed=42)
| Size | Algorithm | Nodes (mean) | Depth (mean) | Time (mean ms) |
|------|-----------|-------------|--------------|----------------|
| 3×3  | BFS       | 73,865      | 21.7         | 140.91         |
| 3×3  | A\*        | 1,564       | 21.7         | 8.57           |
| 3×3  | IDA\*      | 2,062       | —            | 8.75           |
| 4×4  | A\*        | 212         | 18.7         | 1.79           |
| 4×4  | IDA\*      | 177         | —            | 1.28           |

### 4×4 Depth Scaling (50 instances, seed=77)
| Scramble | Sol. Depth | A\* Nodes | IDA\* Nodes | Crossover |
|----------|-----------|----------|------------|----------|
| 10       | 10.0      | 15       | 13         | IDA\* wins |
| 20       | 17.7      | 170      | 153        | IDA\* wins |
| 30       | 25.2      | 3,430    | 4,122      | A\* wins |
| 50       | 34.2      | 214,485  | 122,102*   | A\* wins |
| 75       | —         | —        | —          | IDA\* intractable |

\* 43/50 IDA\* instances solved (others DNF — node limit exceeded)
