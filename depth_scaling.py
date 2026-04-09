"""
Depth-scaling experiment for CS 57200 Phase 2 extension.
Runs A*, IDA*, and BFS on 3x3 puzzles scrambled at depths 10, 20, 30, 50, 75.
50 instances per scramble depth, seed=42.
"""

import json, math, time, random, heapq
from collections import deque

# ── Reuse core functions from solver.py ──────────────────

def goal_state(n): return tuple(range(1, n*n)) + (0,)

def neighbors(state, n):
    bi = state.index(0)
    row, col = divmod(bi, n)
    moves = []
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
        gr, gc = divmod(tile-1, n)
        cr, cc = divmod(idx, n)
        dist += abs(cr-gr) + abs(cc-gc)
    return dist

def generate(n, rng, num_moves):
    state = list(goal_state(n))
    prev = None
    for _ in range(num_moves):
        nbs = [nb for nb in neighbors(tuple(state), n) if tuple(nb) != prev]
        choice = rng.choice(nbs)
        prev = tuple(state)
        state = list(choice)
    return tuple(state)

def bfs(start, n, max_nodes=500_000):
    goal = goal_state(n)
    if start == goal: return {"nodes": 0, "depth": 0, "ms": 0, "found": True}
    frontier = deque([start]); visited = {start: None}; expanded = 0
    t0 = time.perf_counter()
    while frontier:
        s = frontier.popleft(); expanded += 1
        if expanded > max_nodes:
            return {"nodes": expanded, "depth": -1, "ms": (time.perf_counter()-t0)*1000, "found": False}
        for nb in neighbors(s, n):
            if nb not in visited:
                visited[nb] = s
                if nb == goal:
                    depth = 0; cur = nb
                    while visited[cur]: cur = visited[cur]; depth += 1
                    return {"nodes": expanded+1, "depth": depth, "ms": (time.perf_counter()-t0)*1000, "found": True}
                frontier.append(nb)
    return {"nodes": expanded, "depth": -1, "ms": (time.perf_counter()-t0)*1000, "found": False}

def astar(start, n, max_nodes=1_000_000):
    goal = goal_state(n)
    if start == goal: return {"nodes": 0, "depth": 0, "ms": 0, "found": True}
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
            ng = g + 1
            if ng < g_best.get(nb, math.inf):
                g_best[nb] = ng; parent[nb] = s
                heapq.heappush(heap, (ng + manhattan(nb,n), ng, nb))
    return {"nodes": expanded, "depth": -1, "ms": (time.perf_counter()-t0)*1000, "found": False}

def idastar(start, n, max_nodes=500_000):
    goal = goal_state(n)
    counter = [0]
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
        if t == -1: return {"nodes": counter[0], "depth": len(path)-1, "ms": (time.perf_counter()-t0)*1000, "found": True}
        if t == -2 or t == math.inf: return {"nodes": counter[0], "depth": -1, "ms": (time.perf_counter()-t0)*1000, "found": False}
        bound = t

# ── Experiment ───────────────────────────────────────────

SCRAMBLE_DEPTHS = [10, 20, 30, 50, 75]
NUM_INSTANCES   = 50
SEED            = 99

results = {}
rng = random.Random(SEED)

for sd in SCRAMBLE_DEPTHS:
    instances = [generate(3, rng, sd) for _ in range(NUM_INSTANCES)]
    bucket = {"bfs": [], "astar": [], "idastar": []}
    print(f"\nScramble depth {sd} ({NUM_INSTANCES} instances)...")
    for i, state in enumerate(instances):
        print(f"  {i+1}/{NUM_INSTANCES}", end="\r", flush=True)
        bucket["bfs"].append(bfs(state, 3))
        bucket["astar"].append(astar(state, 3))
        bucket["idastar"].append(idastar(state, 3))
    results[str(sd)] = bucket
    # Quick summary
    for algo in ["bfs","astar","idastar"]:
        ns = [r["nodes"] for r in bucket[algo] if r["found"]]
        ds = [r["depth"] for r in bucket[algo] if r["found"]]
        solved = sum(1 for r in bucket[algo] if r["found"])
        mean_n = sum(ns)/len(ns) if ns else 0
        mean_d = sum(ds)/len(ds) if ds else 0
        print(f"  {algo:8s}: solved={solved}/{NUM_INSTANCES}  nodes_mean={mean_n:,.0f}  depth_mean={mean_d:.1f}")

with open("/home/user/workspace/cs57200/depth_scaling_results.json", "w") as f:
    json.dump(results, f, indent=2)
print("\nSaved to depth_scaling_results.json")
