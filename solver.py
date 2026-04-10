"""
CS 57200 – Heuristic Problem Solving
Phase 2: Sliding Tile Puzzle Solver
Algorithms: BFS, A* (Manhattan distance), IDA* (Manhattan distance)
Puzzle sizes: 3x3 (8-puzzle), 4x4 (15-puzzle)
"""

import heapq
import time
import random
import math
from collections import deque
from typing import Optional, List, Dict

# ─────────────────────────────────────────────
# State representation & helpers
# ─────────────────────────────────────────────

def goal_state(n: int) -> tuple:
    return tuple(range(1, n * n)) + (0,)


def blank_index(state: tuple) -> int:
    return state.index(0)


def neighbors(state: tuple, n: int) -> List[tuple]:
    bi = blank_index(state)
    row, col = divmod(bi, n)
    moves = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = row + dr, col + dc
        if 0 <= nr < n and 0 <= nc < n:
            ni = nr * n + nc
            lst = list(state)
            lst[bi], lst[ni] = lst[ni], lst[bi]
            moves.append(tuple(lst))
    return moves


def manhattan_distance(state: tuple, n: int) -> int:
    dist = 0
    for idx, tile in enumerate(state):
        if tile == 0:
            continue
        goal_idx = tile - 1
        goal_row, goal_col = divmod(goal_idx, n)
        cur_row, cur_col = divmod(idx, n)
        dist += abs(cur_row - goal_row) + abs(cur_col - goal_col)
    return dist


def generate_solvable_instance(n: int, rng: random.Random, num_moves: int) -> tuple:
    """Generate instance by making num_moves random moves from goal (always solvable)."""
    state = list(goal_state(n))
    prev = None
    for _ in range(num_moves):
        nbs = [nb for nb in neighbors(tuple(state), n) if tuple(nb) != prev]
        choice = rng.choice(nbs)
        prev = tuple(state)
        state = list(choice)
    return tuple(state)


# ─────────────────────────────────────────────
# BFS
# ─────────────────────────────────────────────

def bfs(start: tuple, n: int, max_nodes: int = 500_000) -> Dict:
    goal = goal_state(n)
    if start == goal:
        return {"nodes_expanded": 0, "depth": 0, "found": True}

    frontier = deque([start])
    visited = {start: None}
    nodes_expanded = 0

    while frontier:
        state = frontier.popleft()
        nodes_expanded += 1
        if nodes_expanded > max_nodes:
            return {"nodes_expanded": nodes_expanded, "depth": -1, "found": False}

        for nb in neighbors(state, n):
            if nb not in visited:
                visited[nb] = state
                if nb == goal:
                    depth = 0
                    cur = nb
                    while visited[cur] is not None:
                        cur = visited[cur]
                        depth += 1
                    return {"nodes_expanded": nodes_expanded + 1,
                            "depth": depth, "found": True}
                frontier.append(nb)

    return {"nodes_expanded": nodes_expanded, "depth": -1, "found": False}


# ─────────────────────────────────────────────
# A* with Manhattan distance
# ─────────────────────────────────────────────

def astar(start: tuple, n: int, max_nodes: int = 1_000_000) -> Dict:
    goal = goal_state(n)
    if start == goal:
        return {"nodes_expanded": 0, "depth": 0, "found": True}

    h_start = manhattan_distance(start, n)
    heap = [(h_start, 0, start)]
    g_best = {start: 0}
    nodes_expanded = 0
    parent = {start: None}

    while heap:
        f, g, state = heapq.heappop(heap)
        if g > g_best.get(state, math.inf):
            continue
        nodes_expanded += 1
        if nodes_expanded > max_nodes:
            return {"nodes_expanded": nodes_expanded, "depth": -1, "found": False}

        if state == goal:
            depth = 0
            cur = state
            while parent[cur] is not None:
                cur = parent[cur]
                depth += 1
            return {"nodes_expanded": nodes_expanded, "depth": depth, "found": True}

        for nb in neighbors(state, n):
            new_g = g + 1
            if new_g < g_best.get(nb, math.inf):
                g_best[nb] = new_g
                parent[nb] = state
                h = manhattan_distance(nb, n)
                heapq.heappush(heap, (new_g + h, new_g, nb))

    return {"nodes_expanded": nodes_expanded, "depth": -1, "found": False}


# ─────────────────────────────────────────────
# IDA* with Manhattan distance
# ─────────────────────────────────────────────

def idastar(start: tuple, n: int, max_nodes: int = 500_000) -> Dict:
    goal = goal_state(n)
    counter = [0]

    def search(path: list, g: int, bound: int) -> int:
        state = path[-1]
        h = manhattan_distance(state, n)
        f = g + h
        if f > bound:
            return f
        if state == goal:
            return -1
        counter[0] += 1
        if counter[0] > max_nodes:
            return -2
        minimum = math.inf
        prev = path[-2] if len(path) >= 2 else None
        for nb in neighbors(state, n):
            if nb == prev:
                continue
            path.append(nb)
            t = search(path, g + 1, bound)
            if t == -1:
                return -1
            if t == -2:
                return -2
            path.pop()
            if t < minimum:
                minimum = t
        return minimum

    bound = manhattan_distance(start, n)
    path = [start]
    while True:
        t = search(path, 0, bound)
        if t == -1:
            return {"nodes_expanded": counter[0], "depth": len(path) - 1, "found": True}
        if t == -2 or t == math.inf:
            return {"nodes_expanded": counter[0], "depth": -1, "found": False}
        bound = t


# ─────────────────────────────────────────────
# Experiment runner
# ─────────────────────────────────────────────

def run_experiment(n: int, instances: list,
                   bfs_limit: int = 500_000,
                   astar_limit: int = 1_000_000,
                   idastar_limit: int = 500_000) -> Dict:
    results = {
        "bfs":     {"nodes": [], "depth": [], "time_ms": [], "solved": 0},
        "astar":   {"nodes": [], "depth": [], "time_ms": [], "solved": 0},
        "idastar": {"nodes": [], "depth": [], "time_ms": [], "solved": 0},
    }

    for i, state in enumerate(instances):
        print(f"  [{n}x{n}] Instance {i+1}/{len(instances)} ...", end="\r", flush=True)

        # ── BFS ──
        if n == 3:
            t0 = time.perf_counter()
            r = bfs(state, n, max_nodes=bfs_limit)
            results["bfs"]["time_ms"].append((time.perf_counter() - t0) * 1000)
            results["bfs"]["nodes"].append(r["nodes_expanded"])
            if r["found"]:
                results["bfs"]["depth"].append(r["depth"])
                results["bfs"]["solved"] += 1
            else:
                results["bfs"]["depth"].append(None)
        else:
            results["bfs"]["nodes"].append(None)
            results["bfs"]["depth"].append(None)
            results["bfs"]["time_ms"].append(None)

        # ── A* ──
        t0 = time.perf_counter()
        r = astar(state, n, max_nodes=astar_limit)
        results["astar"]["time_ms"].append((time.perf_counter() - t0) * 1000)
        results["astar"]["nodes"].append(r["nodes_expanded"])
        if r["found"]:
            results["astar"]["depth"].append(r["depth"])
            results["astar"]["solved"] += 1
        else:
            results["astar"]["depth"].append(None)

        # ── IDA* ──
        t0 = time.perf_counter()
        r = idastar(state, n, max_nodes=idastar_limit)
        results["idastar"]["time_ms"].append((time.perf_counter() - t0) * 1000)
        results["idastar"]["nodes"].append(r["nodes_expanded"])
        if r["found"]:
            results["idastar"]["depth"].append(r["depth"])
            results["idastar"]["solved"] += 1
        else:
            results["idastar"]["depth"].append(None)

    print(f"\n  [{n}x{n}] Done. A* solved {results['astar']['solved']}, IDA* solved {results['idastar']['solved']}")
    return results


def safe_stats(lst):
    vals = [v for v in lst if v is not None]
    if not vals:
        return {"mean": 0, "median": 0, "min": 0, "max": 0}
    vals_sorted = sorted(vals)
    n = len(vals_sorted)
    mid = n // 2
    median = (vals_sorted[mid - 1] + vals_sorted[mid]) / 2.0 if n % 2 == 0 else float(vals_sorted[mid])
    return {
        "mean":   round(sum(vals) / n, 3),
        "median": round(median, 3),
        "min":    round(min(vals), 3),
        "max":    round(max(vals), 3),
        "values": vals,
    }


if __name__ == "__main__":
    import json

    NUM = 100
    SEED = 42
    rng = random.Random(SEED)

    # 3x3: scramble with 50 random moves (gives medium-hard instances)
    instances_3x3 = [generate_solvable_instance(3, rng, 50) for _ in range(NUM)]
    # 4x4: scramble with only 20 moves to keep them tractable for all three solvers
    instances_4x4 = [generate_solvable_instance(4, rng, 20) for _ in range(NUM)]

    print("=== 3x3 (8-puzzle) ===")
    res3 = run_experiment(3, instances_3x3, bfs_limit=500_000,
                          astar_limit=1_000_000, idastar_limit=500_000)

    print("=== 4x4 (15-puzzle) ===")
    res4 = run_experiment(4, instances_4x4, bfs_limit=0,
                          astar_limit=2_000_000, idastar_limit=1_000_000)

    summary = {}
    for label, res, n in [("3x3", res3, 3), ("4x4", res4, 4)]:
        summary[label] = {}
        for algo in ["bfs", "astar", "idastar"]:
            summary[label][algo] = {
                "nodes":   safe_stats(res[algo]["nodes"]),
                "depth":   safe_stats(res[algo]["depth"]),
                "time_ms": safe_stats(res[algo]["time_ms"]),
                "solved":  res[algo]["solved"],
            }

    with open("/home/user/workspace/cs57200/raw_results.json", "w") as f:
        json.dump({"3x3": res3, "4x4": res4}, f, indent=2)

    with open("/home/user/workspace/cs57200/summary.json", "w") as f:
        # Remove 'values' list for summary file
        import copy
        s2 = copy.deepcopy(summary)
        for sz in s2:
            for algo in s2[sz]:
                for metric in ["nodes", "depth", "time_ms"]:
                    s2[sz][algo][metric].pop("values", None)
        json.dump(s2, f, indent=2)

    print("\n=== SUMMARY ===")
    for sz in summary:
        print(f"\n{sz} puzzle:")
        for algo in ["bfs", "astar", "idastar"]:
            d = summary[sz][algo]
            name = algo.upper().replace("ASTAR", "A*").replace("IDASTAR", "IDA*")
            if sz == "4x4" and algo == "bfs":
                print(f"  {name:6s}: N/A (impractical for 4x4)")
                continue
            print(f"  {name:6s}: solved={d['solved']}/100  "
                  f"nodes_mean={d['nodes']['mean']:.0f}  "
                  f"depth_mean={d['depth']['mean']:.1f}  "
                  f"time_mean={d['time_ms']['mean']:.2f}ms")

    print("\nResults saved.")
