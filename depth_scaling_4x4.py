"""
Depth-scaling experiment for 4x4 (15-puzzle).
Scramble depths: 10, 20, 30, 50, 75 — 50 instances each, seed=77.
A* uses a generous limit; IDA* uses a conservative limit to prevent
exponential blowup on deep 4x4 instances.
Unsolved instances are logged as failed (node limit exceeded).
"""

import json, math, time, random, heapq, sys

def goal_state(n): return tuple(range(1, n*n)) + (0,)

def neighbors(state, n):
    bi = state.index(0); row, col = divmod(bi, n); moves = []
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        nr, nc = row+dr, col+dc
        if 0 <= nr < n and 0 <= nc < n:
            ni = nr*n+nc; lst = list(state)
            lst[bi], lst[ni] = lst[ni], lst[bi]
            moves.append(tuple(lst))
    return moves

def manhattan(state, n):
    dist = 0
    for idx, tile in enumerate(state):
        if tile == 0: continue
        gr, gc = divmod(tile-1, n); cr, cc = divmod(idx, n)
        dist += abs(cr-gr) + abs(cc-gc)
    return dist

def generate(n, rng, num_moves):
    state = list(goal_state(n)); prev = None
    for _ in range(num_moves):
        nbs = [nb for nb in neighbors(tuple(state), n) if tuple(nb) != prev]
        choice = rng.choice(nbs); prev = tuple(state); state = list(choice)
    return tuple(state)

def astar(start, n, max_nodes=10_000_000):
    goal = goal_state(n)
    if start == goal: return {"nodes": 0, "depth": 0, "ms": 0.0, "found": True}
    t0 = time.perf_counter()
    heap = [(manhattan(start,n), 0, start)]
    g_best = {start: 0}; parent = {start: None}; expanded = 0
    while heap:
        f, g, s = heapq.heappop(heap)
        if g > g_best.get(s, math.inf): continue
        expanded += 1
        if expanded > max_nodes:
            return {"nodes": expanded, "depth": -1, "ms": (time.perf_counter()-t0)*1000, "found": False}
        if s == goal:
            depth = 0; cur = s
            while parent[cur]: cur = parent[cur]; depth += 1
            return {"nodes": expanded, "depth": depth, "ms": (time.perf_counter()-t0)*1000, "found": True}
        for nb in neighbors(s, n):
            ng = g+1
            if ng < g_best.get(nb, math.inf):
                g_best[nb] = ng; parent[nb] = s
                heapq.heappush(heap, (ng+manhattan(nb,n), ng, nb))
    return {"nodes": expanded, "depth": -1, "ms": (time.perf_counter()-t0)*1000, "found": False}

def idastar(start, n, max_nodes=500_000):
    """IDA* with a node limit to prevent exponential blowup on deep 4x4 instances."""
    goal = goal_state(n); counter = [0]
    t0 = time.perf_counter()
    def search(path, g, bound):
        s = path[-1]; f = g + manhattan(s, n)
        if f > bound: return f
        if s == goal: return -1
        counter[0] += 1
        if counter[0] > max_nodes: return -2
        minimum = math.inf
        prev = path[-2] if len(path) >= 2 else None
        for nb in neighbors(s, n):
            if nb == prev: continue
            path.append(nb); t = search(path, g+1, bound); path.pop()
            if t == -1: return -1
            if t == -2: return -2
            if t < minimum: minimum = t
        return minimum
    bound = manhattan(start, n); path = [start]
    while True:
        t = search(path, 0, bound)
        if t == -1:
            return {"nodes": counter[0], "depth": len(path)-1, "ms": (time.perf_counter()-t0)*1000, "found": True}
        if t == -2 or t == math.inf:
            return {"nodes": counter[0], "depth": -1, "ms": (time.perf_counter()-t0)*1000, "found": False}
        bound = t

# ── Experiment ───────────────────────────────────────────
# Scramble-75 exceeds IDA*'s tractable range for 4x4 with Manhattan-only heuristic.
# We run 10,20,30,50 for full results; 75 is attempted but expected to have DNFs.
SCRAMBLE_DEPTHS = [10, 20, 30, 50, 75]
NUM = 50
SEED = 77

# IDA* node limit per depth tier:
# shallow depths it easily solves; deeper ones hit the budget and are logged as DNF
IDASTAR_LIMITS = {10: 500_000, 20: 500_000, 30: 1_000_000,
                  50: 1_000_000, 75: 200_000}   # 75: small limit, expect many DNFs
ASTAR_LIMIT = 10_000_000

results = {}
rng = random.Random(SEED)

for sd in SCRAMBLE_DEPTHS:
    instances = [generate(4, rng, sd) for _ in range(NUM)]
    bucket = {"astar": [], "idastar": []}
    print(f"\n=== Scramble depth {sd} ===")

    for i, state in enumerate(instances):
        print(f"  {i+1}/{NUM}", end="\r", flush=True)
        sys.stdout.flush()
        bucket["astar"].append(astar(state, 4, max_nodes=ASTAR_LIMIT))
        bucket["idastar"].append(idastar(state, 4, max_nodes=IDASTAR_LIMITS[sd]))

    results[str(sd)] = bucket

    # Save incrementally after every tier so a timeout doesn't lose data
    with open("/home/user/workspace/cs57200/depth_scaling_4x4_results.json","w") as f:
        json.dump(results, f, indent=2)

    for algo in ["astar","idastar"]:
        sv  = sum(1 for r in bucket[algo] if r["found"])
        ns  = [r["nodes"] for r in bucket[algo] if r["found"]]
        ds  = [r["depth"] for r in bucket[algo] if r["found"] and r["depth"]>=0]
        ts  = [r["ms"]    for r in bucket[algo] if r["found"]]
        print(f"  {algo:8s}: solved={sv}/{NUM}  "
              f"nodes_mean={sum(ns)/len(ns) if ns else 0:,.0f}  "
              f"depth_mean={sum(ds)/len(ds) if ds else 0:.1f}  "
              f"time_mean={sum(ts)/len(ts) if ts else 0:.2f} ms")

with open("/home/user/workspace/cs57200/depth_scaling_4x4_results.json","w") as f:
    json.dump(results, f, indent=2)
print("\nSaved to depth_scaling_4x4_results.json")
