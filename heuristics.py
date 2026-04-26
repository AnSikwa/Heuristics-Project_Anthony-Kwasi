"""
CS 57200 - Heuristic Problem Solving
Heuristics module for sliding-tile puzzles.

This module provides admissible heuristic functions used by A* and IDA*:

    - Manhattan distance (baseline)
    - Manhattan + Linear Conflict (Hansson, Mayer & Yung 1992)
    - Disjoint Pattern Database lookup (Korf & Felner 2002)

All heuristics are admissible (never overestimate true cost). Manhattan
and Manhattan+Linear-Conflict are also consistent. Disjoint additive
PDBs are admissible because each tile move advances at most one tile,
so per-group costs can be summed without inflating the estimate.
"""

from collections import deque
from typing import Dict, Iterable, Tuple


# ────────────────────────────────────────────────────────────────────
# Manhattan distance
# ────────────────────────────────────────────────────────────────────

def manhattan_distance(state: Tuple[int, ...], n: int) -> int:
    """
    Sum of Manhattan distances from each non-blank tile to its goal cell.

    Manhattan distance is the exact cost of a relaxed problem in which
    tiles may overlap, so it is admissible and consistent.

    Args:
        state: Flat tuple of length n*n; 0 is the blank.
        n: Board side length (3 for 8-puzzle, 4 for 15-puzzle).

    Returns:
        Total Manhattan distance (>= 0).
    """
    dist = 0
    for idx, tile in enumerate(state):
        if tile == 0:
            continue
        goal_idx = tile - 1
        goal_row, goal_col = divmod(goal_idx, n)
        cur_row, cur_col = divmod(idx, n)
        dist += abs(cur_row - goal_row) + abs(cur_col - goal_col)
    return dist


# ────────────────────────────────────────────────────────────────────
# Linear Conflict
# ────────────────────────────────────────────────────────────────────

def linear_conflict(state: Tuple[int, ...], n: int) -> int:
    """
    Manhattan distance + 2 * (linear conflicts in rows and columns).

    Two tiles a, b are in linear conflict when they are both in their
    goal row (or column) but their relative order is reversed with
    respect to the goal. Each conflict forces one tile to move out of
    the line and back, adding at least 2 moves. Adding 2 per conflict
    keeps the heuristic admissible (Hansson, Mayer & Yung, 1992).

    Args:
        state: Flat tuple of length n*n.
        n: Board side length.

    Returns:
        Manhattan distance plus 2 times the number of linear conflicts.
    """
    md = manhattan_distance(state, n)
    conflicts = 0

    # Row conflicts.
    for r in range(n):
        row_tiles = []
        for c in range(n):
            t = state[r * n + c]
            if t == 0:
                continue
            goal_r, goal_c = divmod(t - 1, n)
            if goal_r == r:
                row_tiles.append((c, goal_c))
        conflicts += _count_line_conflicts(row_tiles)

    # Column conflicts.
    for c in range(n):
        col_tiles = []
        for r in range(n):
            t = state[r * n + c]
            if t == 0:
                continue
            goal_r, goal_c = divmod(t - 1, n)
            if goal_c == c:
                col_tiles.append((r, goal_r))
        conflicts += _count_line_conflicts(col_tiles)

    return md + 2 * conflicts


def _count_line_conflicts(line) -> int:
    """
    Greedy admissible count of linear conflicts in a single row/column.

    Repeatedly removes the tile with the largest number of inversions
    until the line is conflict-free, returning the total removals.

    Args:
        line: list of (current_pos, goal_pos) tuples for tiles in this
            line that belong in this line.

    Returns:
        Number of conflicts (each contributes 2 to the heuristic bonus).
    """
    if len(line) < 2:
        return 0
    items = list(line)
    conflicts = 0
    while True:
        max_idx = -1
        max_inv = 0
        for i, (pos_i, goal_i) in enumerate(items):
            inv = 0
            for j, (pos_j, goal_j) in enumerate(items):
                if i == j:
                    continue
                if pos_i < pos_j and goal_i > goal_j:
                    inv += 1
                elif pos_i > pos_j and goal_i < goal_j:
                    inv += 1
            if inv > max_inv:
                max_inv = inv
                max_idx = i
        if max_inv == 0:
            return conflicts
        items.pop(max_idx)
        conflicts += 1


# ────────────────────────────────────────────────────────────────────
# Disjoint Pattern Databases
# ────────────────────────────────────────────────────────────────────
#
# Korf & Felner (2002) introduced disjoint additive PDBs: tile groups
# are partitioned so that no tile appears in more than one group, and
# each PDB stores the minimum number of GROUP-tile moves needed to
# return every group-tile to its goal cell. Because each move advances
# at most one tile, per-group costs are additive and the sum is
# admissible.
#
# We expose two partitions:
#   - GROUPS_4_4_8PUZZLE for the 3x3 (8-puzzle): two 4-tile groups.
#     Build time in pure Python is on the order of seconds.
#   - GROUPS_5_5_5 for the 4x4 (15-puzzle): three 5-tile groups.
#     Build time in pure Python is large; M2's contingency plan cited
#     this exact tradeoff.
# ────────────────────────────────────────────────────────────────────

# 5-5-5 partition is the canonical Korf-Felner partition for the
# 15-puzzle, but it requires ~17M entries which is impractical to build
# in pure Python. We expose it for completeness and use the more
# tractable 4-4-4-3 partition (~1.6M entries, builds in seconds) for
# experiments.
GROUPS_5_5_5 = (
    (1, 2, 3, 4, 5),
    (6, 7, 8, 9, 10),
    (11, 12, 13, 14, 15),
)

GROUPS_4_4_4_3 = (
    (1, 2, 5, 6),
    (3, 4, 7, 8),
    (9, 10, 13, 14),
    (11, 12, 15),
)

GROUPS_4_4_8PUZZLE = (
    (1, 2, 3, 4),
    (5, 6, 7, 8),
)


def _goal_state_for(n: int) -> Tuple[int, ...]:
    """Canonical goal state for the n-by-n sliding puzzle."""
    return tuple(range(1, n * n)) + (0,)


def build_pdb(group: Tuple[int, ...], n: int = 4) -> Dict:
    """
    Build a disjoint additive PDB by 0-1 BFS from the goal in projected
    space.

    Each PDB key is (blank_idx, (idx_of_t1, ..., idx_of_tk)) where the
    tile indices are the 0-based positions of the group tiles on the
    board. Successors are generated by sliding the blank into one of
    its neighbours; the step cost is 1 if a group tile is displaced and
    0 otherwise. We use a 0-1 BFS (deque appendleft for cost-0 edges,
    append for cost-1 edges) which yields optimal distances in O(V+E).

    Args:
        group: tuple of tile values defining the partition.
        n: board side length (3 or 4).

    Returns:
        Dict mapping projected key -> minimum group-move cost.
    """
    NB = n * n
    neighbours = []
    for i in range(NB):
        r, c = divmod(i, n)
        adj = []
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n:
                adj.append(nr * n + nc)
        neighbours.append(tuple(adj))

    goal_positions = tuple((t - 1) for t in group)
    goal_blank = NB - 1
    start_key = (goal_blank, goal_positions)
    table: Dict = {start_key: 0}
    deq = deque([start_key])

    while deq:
        key = deq.popleft()
        cost = table[key]
        blank_idx, positions = key
        # Map cell -> slot in `positions` for O(1) ownership lookup.
        cell_owner = {cell: slot for slot, cell in enumerate(positions)}
        for new_blank in neighbours[blank_idx]:
            if new_blank in cell_owner:
                slot = cell_owner[new_blank]
                new_positions = list(positions)
                new_positions[slot] = blank_idx
                new_key = (new_blank, tuple(new_positions))
                new_cost = cost + 1
                prev = table.get(new_key)
                if prev is None or new_cost < prev:
                    table[new_key] = new_cost
                    deq.append(new_key)
            else:
                new_key = (new_blank, positions)
                prev = table.get(new_key)
                if prev is None or cost < prev:
                    table[new_key] = cost
                    deq.appendleft(new_key)
    return table


def _project(state: Tuple[int, ...], group: Tuple[int, ...]) -> Tuple:
    """
    Project a full puzzle state onto a tile group.

    Returns (blank_idx, tuple of board-indices of group tiles in order).
    """
    pos = [0] * len(group)
    blank_idx = 0
    rev = {t: i for i, t in enumerate(group)}
    for idx, t in enumerate(state):
        if t == 0:
            blank_idx = idx
        elif t in rev:
            pos[rev[t]] = idx
    return (blank_idx, tuple(pos))


def pdb_lookup(state: Tuple[int, ...], pdbs: Iterable[Dict],
               groups: Tuple[Tuple[int, ...], ...] = GROUPS_5_5_5) -> int:
    """
    Sum PDB lookups across disjoint tile groups.

    Args:
        state: full puzzle state.
        pdbs: iterable of PDB dicts in the same order as `groups`.
        groups: tuple of group tuples matching the PDBs.

    Returns:
        Sum of group costs (admissible because the groups are disjoint).
    """
    total = 0
    for pdb, group in zip(pdbs, groups):
        key = _project(state, group)
        total += pdb.get(key, 0)
    return total


def make_pdb_heuristic(pdbs, groups, n: int):
    """
    Build a heuristic function `h(state)` that combines the PDB lookup
    with Manhattan distance over the blank-only tiles (none in the
    standard partitions, so this just returns the PDB sum).

    Args:
        pdbs: list of PDB dicts.
        groups: tuple of tile-group tuples.
        n: board side length.

    Returns:
        Callable taking a state tuple and returning an admissible
        heuristic value.
    """
    def h(state: Tuple[int, ...]) -> int:
        return pdb_lookup(state, pdbs, groups)
    return h
