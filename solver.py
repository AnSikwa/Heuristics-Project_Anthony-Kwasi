"""
CS 57200 - Heuristic Problem Solving
Sliding Tile Puzzle Solver: BFS, A*, IDA*

This module exposes the core search algorithms used in the Phase 2 and
Phase 3 experiments. Each search returns a uniform result dict with
keys ``nodes_expanded``, ``depth``, and ``found``.

Heuristics live in ``heuristics.py`` (Manhattan, Linear Conflict,
Disjoint PDB). Algorithms accept a heuristic callable so the same
search code is reused across all enhancements.

Algorithms:
    - BFS (uninformed baseline; uses no heuristic)
    - A* with a pluggable heuristic
    - IDA* with a pluggable heuristic

Puzzle sizes: 3x3 (8-puzzle) and 4x4 (15-puzzle).
"""

import heapq
import math
import random
import time
from collections import deque
from typing import Callable, Dict, List, Optional, Tuple

from heuristics import manhattan_distance


# ─────────────────────────────────────────────────────────────
# State representation & helpers
# ─────────────────────────────────────────────────────────────

def goal_state(n: int) -> tuple:
    """Canonical goal state: (1, 2, ..., n*n - 1, 0)."""
    return tuple(range(1, n * n)) + (0,)


def blank_index(state: tuple) -> int:
    """Return the index of the blank (0) in the flat state tuple."""
    return state.index(0)


def neighbors(state: tuple, n: int) -> List[tuple]:
    """
    Generate all states reachable by sliding the blank one cell.

    Args:
        state: current flat state tuple of length n*n.
        n: board side length.

    Returns:
        List of successor state tuples (up to 4).
    """
    bi = blank_index(state)
    row, col = divmod(bi, n)
    out = []
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nr, nc = row + dr, col + dc
        if 0 <= nr < n and 0 <= nc < n:
            ni = nr * n + nc
            lst = list(state)
            lst[bi], lst[ni] = lst[ni], lst[bi]
            out.append(tuple(lst))
    return out


def generate_solvable_instance(n: int, rng: random.Random,
                               num_moves: int) -> tuple:
    """
    Generate a solvable puzzle instance via random walk from the goal.

    Each move is chosen uniformly at random from legal blank moves,
    excluding the immediate predecessor to avoid trivial back-tracking.
    Any state reachable from the goal by legal moves is solvable, so
    no parity check is required.

    Args:
        n: board side length.
        rng: seeded ``random.Random`` for reproducibility.
        num_moves: scramble depth (number of random moves from goal).

    Returns:
        Solvable state tuple.
    """
    state = list(goal_state(n))
    prev: Optional[tuple] = None
    for _ in range(num_moves):
        candidates = [nb for nb in neighbors(tuple(state), n)
                      if tuple(nb) != prev]
        choice = rng.choice(candidates)
        prev = tuple(state)
        state = list(choice)
    return tuple(state)


# ─────────────────────────────────────────────────────────────
# BFS
# ─────────────────────────────────────────────────────────────

def bfs(start: tuple, n: int, max_nodes: int = 500_000) -> Dict:
    """
    Breadth-first search from ``start`` to the goal state.

    BFS is used as the uninformed baseline. Because edge costs are
    uniform, BFS returns an optimal-length path. It is impractical on
    the 4x4 puzzle for non-trivial scrambles.

    Args:
        start: start state tuple.
        n: board side length.
        max_nodes: hard cap on nodes expanded; if exceeded the search
            returns ``found=False``.

    Returns:
        Dict with keys ``nodes_expanded``, ``depth`` (or -1 if unsolved)
        and ``found``.
    """
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
            return {"nodes_expanded": nodes_expanded, "depth": -1,
                    "found": False}

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


# ─────────────────────────────────────────────────────────────
# A* with pluggable heuristic
# ─────────────────────────────────────────────────────────────

def astar(start: tuple, n: int,
          heuristic: Optional[Callable[[tuple, int], int]] = None,
          max_nodes: int = 1_000_000) -> Dict:
    """
    A* search with a pluggable admissible heuristic.

    Implementation notes:
        - Uses a binary heap ordered by (f, g, state) where f = g + h.
        - Lazy deletion: outdated heap entries are skipped when popped.
        - Tie-breaking: heap order breaks ties by lower g first because
          tuples compare lexicographically; this preserves admissibility.

    Args:
        start: start state tuple.
        n: board side length.
        heuristic: callable ``h(state, n) -> int``. Defaults to Manhattan
            distance if None.
        max_nodes: hard cap on nodes expanded.

    Returns:
        Result dict (see ``bfs`` docstring).
    """
    if heuristic is None:
        heuristic = manhattan_distance
    goal = goal_state(n)
    if start == goal:
        return {"nodes_expanded": 0, "depth": 0, "found": True}

    h_start = heuristic(start, n)
    heap = [(h_start, 0, start)]
    g_best = {start: 0}
    parent = {start: None}
    nodes_expanded = 0

    while heap:
        f, g, state = heapq.heappop(heap)
        if g > g_best.get(state, math.inf):
            continue
        nodes_expanded += 1
        if nodes_expanded > max_nodes:
            return {"nodes_expanded": nodes_expanded, "depth": -1,
                    "found": False}

        if state == goal:
            depth = 0
            cur = state
            while parent[cur] is not None:
                cur = parent[cur]
                depth += 1
            return {"nodes_expanded": nodes_expanded, "depth": depth,
                    "found": True}

        for nb in neighbors(state, n):
            new_g = g + 1
            if new_g < g_best.get(nb, math.inf):
                g_best[nb] = new_g
                parent[nb] = state
                h = heuristic(nb, n)
                heapq.heappush(heap, (new_g + h, new_g, nb))

    return {"nodes_expanded": nodes_expanded, "depth": -1, "found": False}


# ─────────────────────────────────────────────────────────────
# IDA* with pluggable heuristic
# ─────────────────────────────────────────────────────────────

def idastar(start: tuple, n: int,
            heuristic: Optional[Callable[[tuple, int], int]] = None,
            max_nodes: int = 500_000) -> Dict:
    """
    Iterative-Deepening A* with a pluggable admissible heuristic.

    IDA* runs a sequence of depth-first searches bounded by an
    f-threshold that increases to the next-smallest f-value after each
    failed iteration. Memory use is O(d) which makes IDA* applicable
    to the 4x4 puzzle where A* exhausts memory.

    Implementation notes:
        - ``parent pruning``: we skip the immediate predecessor so the
          search does not oscillate.
        - The recursion uses a Python list as a stack for the path; for
          deep 4x4 instances we set ``sys.setrecursionlimit`` upstream.

    Args:
        start: start state tuple.
        n: board side length.
        heuristic: callable ``h(state, n) -> int``. Defaults to Manhattan.
        max_nodes: cap on total node expansions across all iterations.

    Returns:
        Result dict (see ``bfs`` docstring).
    """
    if heuristic is None:
        heuristic = manhattan_distance
    goal = goal_state(n)
    counter = [0]

    def search(path: list, g: int, bound: int) -> int:
        state = path[-1]
        h = heuristic(state, n)
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
            path.pop()
            if t == -1:
                return -1
            if t == -2:
                return -2
            if t < minimum:
                minimum = t
        return minimum

    bound = heuristic(start, n)
    path = [start]
    while True:
        t = search(path, 0, bound)
        if t == -1:
            return {"nodes_expanded": counter[0],
                    "depth": len(path) - 1, "found": True}
        if t == -2 or t == math.inf:
            return {"nodes_expanded": counter[0], "depth": -1,
                    "found": False}
        bound = t


# ─────────────────────────────────────────────────────────────
# Phase 2 experiment runner (kept for backward compatibility)
# ─────────────────────────────────────────────────────────────

def run_experiment(n: int, instances: list,
                   bfs_limit: int = 500_000,
                   astar_limit: int = 1_000_000,
                   idastar_limit: int = 500_000) -> Dict:
    """
    Run BFS, A*, and IDA* (all with Manhattan distance) on each instance.

    Used by the original Phase 2 experiment; Phase 3 ablations live in
    ``ablation.py``.

    Args:
        n: board side length.
        instances: list of state tuples.
        bfs_limit: BFS node cap.
        astar_limit: A* node cap.
        idastar_limit: IDA* node cap.

    Returns:
        Dict with per-algorithm aggregated lists of ``nodes``, ``depth``,
        ``time_ms`` and a ``solved`` count.
    """
    results = {
        "bfs":     {"nodes": [], "depth": [], "time_ms": [], "solved": 0},
        "astar":   {"nodes": [], "depth": [], "time_ms": [], "solved": 0},
        "idastar": {"nodes": [], "depth": [], "time_ms": [], "solved": 0},
    }

    for i, state in enumerate(instances):
        print(f"  [{n}x{n}] Instance {i+1}/{len(instances)} ...",
              end="\r", flush=True)

        if n == 3:
            t0 = time.perf_counter()
            r = bfs(state, n, max_nodes=bfs_limit)
            results["bfs"]["time_ms"].append(
                (time.perf_counter() - t0) * 1000)
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

        t0 = time.perf_counter()
        r = astar(state, n, max_nodes=astar_limit)
        results["astar"]["time_ms"].append(
            (time.perf_counter() - t0) * 1000)
        results["astar"]["nodes"].append(r["nodes_expanded"])
        if r["found"]:
            results["astar"]["depth"].append(r["depth"])
            results["astar"]["solved"] += 1
        else:
            results["astar"]["depth"].append(None)

        t0 = time.perf_counter()
        r = idastar(state, n, max_nodes=idastar_limit)
        results["idastar"]["time_ms"].append(
            (time.perf_counter() - t0) * 1000)
        results["idastar"]["nodes"].append(r["nodes_expanded"])
        if r["found"]:
            results["idastar"]["depth"].append(r["depth"])
            results["idastar"]["solved"] += 1
        else:
            results["idastar"]["depth"].append(None)

    print(f"\n  [{n}x{n}] Done. A* solved {results['astar']['solved']}, "
          f"IDA* solved {results['idastar']['solved']}")
    return results


def safe_stats(lst):
    """
    Return summary stats for a list, ignoring None values.

    Args:
        lst: iterable of numeric values or None.

    Returns:
        Dict with ``mean``, ``median``, ``min``, ``max`` keys.
    """
    vals = [v for v in lst if v is not None]
    if not vals:
        return {"mean": 0, "median": 0, "min": 0, "max": 0}
    vals_sorted = sorted(vals)
    return {
        "mean": sum(vals) / len(vals),
        "median": vals_sorted[len(vals) // 2],
        "min": min(vals),
        "max": max(vals),
    }


# ─────────────────────────────────────────────────────────────
# Main entry: replicates Phase 2 results.
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json
    import os

    SEED = 42
    OUT = "raw_results.json"
    rng = random.Random(SEED)

    print("Generating 100 3x3 instances (50-move scramble)...")
    inst3 = [generate_solvable_instance(3, rng, 50) for _ in range(100)]
    print("Generating 100 4x4 instances (20-move scramble)...")
    inst4 = [generate_solvable_instance(4, rng, 20) for _ in range(100)]

    print("\nRunning 3x3 experiments...")
    res3 = run_experiment(3, inst3)
    print("Running 4x4 experiments...")
    res4 = run_experiment(4, inst4, bfs_limit=0)

    summary = {
        "seed": SEED,
        "3x3": {alg: {"stats": safe_stats(d["nodes"]),
                      "depth_stats": safe_stats(d["depth"]),
                      "time_stats": safe_stats(d["time_ms"]),
                      "solved": d["solved"]}
                for alg, d in res3.items()},
        "4x4": {alg: {"stats": safe_stats(d["nodes"]),
                      "depth_stats": safe_stats(d["depth"]),
                      "time_stats": safe_stats(d["time_ms"]),
                      "solved": d["solved"]}
                for alg, d in res4.items()},
    }
    with open(OUT, "w") as f:
        json.dump({"raw3": res3, "raw4": res4, "summary": summary}, f,
                  indent=2, default=str)
    print(f"\nResults saved to {OUT}")
