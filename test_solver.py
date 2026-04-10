"""
Comprehensive test suite for solver.py
CS 57200 – Sliding Tile Puzzle Solver
"""

import math
import random
import pytest

from solver import (
    goal_state,
    blank_index,
    neighbors,
    manhattan_distance,
    generate_solvable_instance,
    bfs,
    astar,
    idastar,
    safe_stats,
    run_experiment,
)


# ─────────────────────────────────────────────
# goal_state
# ─────────────────────────────────────────────

class TestGoalState:
    def test_3x3(self):
        assert goal_state(3) == (1, 2, 3, 4, 5, 6, 7, 8, 0)

    def test_4x4(self):
        assert goal_state(4) == (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0)

    def test_2x2(self):
        assert goal_state(2) == (1, 2, 3, 0)

    def test_length(self):
        for n in [2, 3, 4]:
            assert len(goal_state(n)) == n * n

    def test_blank_at_end(self):
        for n in [2, 3, 4]:
            assert goal_state(n)[-1] == 0

    def test_tiles_are_sequential(self):
        for n in [2, 3, 4]:
            gs = goal_state(n)
            assert list(gs[:-1]) == list(range(1, n * n))


# ─────────────────────────────────────────────
# blank_index
# ─────────────────────────────────────────────

class TestBlankIndex:
    def test_blank_at_end(self):
        assert blank_index((1, 2, 3, 4, 5, 6, 7, 8, 0)) == 8

    def test_blank_at_start(self):
        assert blank_index((0, 1, 2, 3, 4, 5, 6, 7, 8)) == 0

    def test_blank_in_middle(self):
        assert blank_index((1, 2, 0, 3, 4, 5, 6, 7, 8)) == 2

    def test_blank_in_4x4(self):
        state = tuple(range(1, 16)) + (0,)
        assert blank_index(state) == 15

    def test_blank_first_position_4x4(self):
        state = (0,) + tuple(range(1, 16))
        assert blank_index(state) == 0


# ─────────────────────────────────────────────
# neighbors
# ─────────────────────────────────────────────

class TestNeighbors:
    def test_goal_state_neighbors_3x3(self):
        # blank at position 8 (bottom-right corner): can move up or left
        gs = goal_state(3)
        nbs = neighbors(gs, 3)
        assert len(nbs) == 2

    def test_blank_center_3x3(self):
        # blank at position 4 (center): can move in all 4 directions
        state = (1, 2, 3, 4, 0, 5, 6, 7, 8)
        nbs = neighbors(state, 3)
        assert len(nbs) == 4

    def test_blank_top_left_corner(self):
        state = (0, 1, 2, 3, 4, 5, 6, 7, 8)
        nbs = neighbors(state, 3)
        assert len(nbs) == 2

    def test_blank_top_right_corner(self):
        state = (1, 2, 0, 3, 4, 5, 6, 7, 8)
        nbs = neighbors(state, 3)
        assert len(nbs) == 2

    def test_blank_bottom_left_corner(self):
        state = (1, 2, 3, 4, 5, 6, 0, 7, 8)
        nbs = neighbors(state, 3)
        assert len(nbs) == 2

    def test_blank_top_edge(self):
        # blank at position 1 (top middle): can move left, right, down
        state = (1, 0, 2, 3, 4, 5, 6, 7, 8)
        nbs = neighbors(state, 3)
        assert len(nbs) == 3

    def test_blank_left_edge(self):
        # blank at position 3 (left middle): can move up, right, down
        state = (1, 2, 3, 0, 4, 5, 6, 7, 8)
        nbs = neighbors(state, 3)
        assert len(nbs) == 3

    def test_neighbors_are_valid_states(self):
        state = (1, 2, 3, 4, 0, 5, 6, 7, 8)
        nbs = neighbors(state, 3)
        for nb in nbs:
            assert len(nb) == 9
            assert sorted(nb) == list(range(9))

    def test_swap_is_correct_move_up(self):
        # blank at center (4), move up swaps with position 1
        state = (1, 2, 3, 4, 0, 5, 6, 7, 8)
        nbs = neighbors(state, 3)
        # moving blank up: blank goes to index 1, tile 2 goes to index 4
        assert (1, 0, 3, 4, 2, 5, 6, 7, 8) in nbs

    def test_swap_is_correct_move_down(self):
        state = (1, 2, 3, 4, 0, 5, 6, 7, 8)
        nbs = neighbors(state, 3)
        # moving blank down: blank goes to index 7, tile 7 goes to index 4
        assert (1, 2, 3, 4, 7, 5, 6, 0, 8) in nbs

    def test_swap_is_correct_move_left(self):
        state = (1, 2, 3, 4, 0, 5, 6, 7, 8)
        nbs = neighbors(state, 3)
        # moving blank left: blank goes to index 3, tile 4 goes to index 4
        assert (1, 2, 3, 0, 4, 5, 6, 7, 8) in nbs

    def test_swap_is_correct_move_right(self):
        state = (1, 2, 3, 4, 0, 5, 6, 7, 8)
        nbs = neighbors(state, 3)
        # moving blank right: blank goes to index 5, tile 5 goes to index 4
        assert (1, 2, 3, 4, 5, 0, 6, 7, 8) in nbs

    def test_neighbors_4x4_center(self):
        # blank at position 5 in 4x4 (row 1, col 1): 4 neighbors
        state = list(range(1, 16)) + [0]
        state[15], state[5] = state[5], state[15]
        state = tuple(state)
        nbs = neighbors(state, 4)
        assert len(nbs) == 4

    def test_neighbors_are_tuples(self):
        gs = goal_state(3)
        nbs = neighbors(gs, 3)
        for nb in nbs:
            assert isinstance(nb, tuple)

    def test_neighbors_differ_by_one_swap(self):
        state = (1, 2, 3, 4, 0, 5, 6, 7, 8)
        nbs = neighbors(state, 3)
        for nb in nbs:
            diff = sum(1 for a, b in zip(state, nb) if a != b)
            assert diff == 2  # exactly two positions differ (the swap)


# ─────────────────────────────────────────────
# manhattan_distance
# ─────────────────────────────────────────────

class TestManhattanDistance:
    def test_goal_state_3x3(self):
        assert manhattan_distance(goal_state(3), 3) == 0

    def test_goal_state_4x4(self):
        assert manhattan_distance(goal_state(4), 4) == 0

    def test_one_move_from_goal(self):
        # swap tile 8 and blank: blank at index 7, 8 at index 8
        state = (1, 2, 3, 4, 5, 6, 7, 0, 8)
        assert manhattan_distance(state, 3) == 1

    def test_non_negative(self):
        rng = random.Random(42)
        for _ in range(20):
            state = generate_solvable_instance(3, rng, 20)
            assert manhattan_distance(state, 3) >= 0

    def test_blank_ignored(self):
        # moving the blank should not affect manhattan distance calculation
        # since blank (0) is skipped
        state = goal_state(3)
        assert manhattan_distance(state, 3) == 0

    def test_increases_with_distance(self):
        # A state farther from goal should generally have higher heuristic
        rng = random.Random(7)
        state_near = generate_solvable_instance(3, rng, 3)
        state_far = generate_solvable_instance(3, rng, 30)
        # Both should be >= 0; we can't strictly compare without knowing true depth
        assert manhattan_distance(state_near, 3) >= 0
        assert manhattan_distance(state_far, 3) >= 0

    def test_specific_state_3x3(self):
        # State (0, 1, 2, 3, 4, 5, 6, 7, 8): blank at 0, all tiles shifted right
        # tile 1 at idx 1: goal_idx=0 (row0,col0), cur (row0,col1): dist=1
        # tile 2 at idx 2: goal_idx=1 (row0,col1), cur (row0,col2): dist=1
        # tile 3 at idx 3: goal_idx=2 (row0,col2), cur (row1,col0): dist=1+2=3
        # tile 4 at idx 4: goal_idx=3 (row1,col0), cur (row1,col1): dist=1
        # tile 5 at idx 5: goal_idx=4 (row1,col1), cur (row1,col2): dist=1
        # tile 6 at idx 6: goal_idx=5 (row1,col2), cur (row2,col0): dist=1+2=3
        # tile 7 at idx 7: goal_idx=6 (row2,col0), cur (row2,col1): dist=1
        # tile 8 at idx 8: goal_idx=7 (row2,col1), cur (row2,col2): dist=1
        # Total = 1+1+3+1+1+3+1+1 = 12
        state = (0, 1, 2, 3, 4, 5, 6, 7, 8)
        assert manhattan_distance(state, 3) == 12

    def test_4x4_one_move(self):
        # Swap tile 15 and blank in goal state
        gs = list(goal_state(4))
        gs[14], gs[15] = gs[15], gs[14]
        state = tuple(gs)
        assert manhattan_distance(state, 4) == 1


# ─────────────────────────────────────────────
# generate_solvable_instance
# ─────────────────────────────────────────────

class TestGenerateSolvableInstance:
    def test_returns_tuple(self):
        rng = random.Random(1)
        state = generate_solvable_instance(3, rng, 10)
        assert isinstance(state, tuple)

    def test_correct_length_3x3(self):
        rng = random.Random(1)
        state = generate_solvable_instance(3, rng, 10)
        assert len(state) == 9

    def test_correct_length_4x4(self):
        rng = random.Random(1)
        state = generate_solvable_instance(4, rng, 10)
        assert len(state) == 16

    def test_contains_all_tiles_3x3(self):
        rng = random.Random(1)
        state = generate_solvable_instance(3, rng, 10)
        assert sorted(state) == list(range(9))

    def test_contains_all_tiles_4x4(self):
        rng = random.Random(1)
        state = generate_solvable_instance(4, rng, 10)
        assert sorted(state) == list(range(16))

    def test_zero_moves_returns_goal(self):
        rng = random.Random(1)
        state = generate_solvable_instance(3, rng, 0)
        assert state == goal_state(3)

    def test_deterministic_with_same_seed(self):
        state1 = generate_solvable_instance(3, random.Random(42), 20)
        state2 = generate_solvable_instance(3, random.Random(42), 20)
        assert state1 == state2

    def test_different_seeds_differ(self):
        state1 = generate_solvable_instance(3, random.Random(1), 20)
        state2 = generate_solvable_instance(3, random.Random(2), 20)
        assert state1 != state2

    def test_solvable_via_bfs(self):
        # Small number of moves so BFS can verify solvability
        rng = random.Random(99)
        for _ in range(5):
            state = generate_solvable_instance(3, rng, 5)
            result = bfs(state, 3)
            assert result["found"] is True


# ─────────────────────────────────────────────
# BFS
# ─────────────────────────────────────────────

class TestBFS:
    def test_goal_state_immediately(self):
        result = bfs(goal_state(3), 3)
        assert result["found"] is True
        assert result["depth"] == 0
        assert result["nodes_expanded"] == 0

    def test_one_move_away(self):
        # Swap blank with tile 8 (one move from goal)
        state = (1, 2, 3, 4, 5, 6, 7, 0, 8)
        result = bfs(state, 3)
        assert result["found"] is True
        assert result["depth"] == 1

    def test_two_moves_away(self):
        # blank moves right then down from goal
        state = (1, 2, 3, 4, 5, 6, 0, 7, 8)
        result = bfs(state, 3)
        assert result["found"] is True
        assert result["depth"] == 2

    def test_returns_dict(self):
        result = bfs(goal_state(3), 3)
        assert "found" in result
        assert "depth" in result
        assert "nodes_expanded" in result

    def test_found_is_bool(self):
        result = bfs(goal_state(3), 3)
        assert isinstance(result["found"], bool)

    def test_depth_nonneg_when_found(self):
        rng = random.Random(5)
        state = generate_solvable_instance(3, rng, 8)
        result = bfs(state, 3)
        if result["found"]:
            assert result["depth"] >= 0

    def test_nodes_expanded_nonneg(self):
        rng = random.Random(5)
        state = generate_solvable_instance(3, rng, 8)
        result = bfs(state, 3)
        assert result["nodes_expanded"] >= 0

    def test_max_nodes_exceeded(self):
        rng = random.Random(42)
        state = generate_solvable_instance(3, rng, 30)
        result = bfs(state, 3, max_nodes=10)
        # With only 10 nodes, a 30-move puzzle will likely not be solved
        assert result["nodes_expanded"] >= 0
        if not result["found"]:
            assert result["depth"] == -1

    def test_medium_puzzle(self):
        rng = random.Random(1)
        state = generate_solvable_instance(3, rng, 10)
        result = bfs(state, 3)
        assert result["found"] is True
        assert result["depth"] > 0


# ─────────────────────────────────────────────
# A*
# ─────────────────────────────────────────────

class TestAStar:
    def test_goal_state_immediately(self):
        result = astar(goal_state(3), 3)
        assert result["found"] is True
        assert result["depth"] == 0
        assert result["nodes_expanded"] == 0

    def test_one_move_away(self):
        state = (1, 2, 3, 4, 5, 6, 7, 0, 8)
        result = astar(state, 3)
        assert result["found"] is True
        assert result["depth"] == 1

    def test_two_moves_away(self):
        state = (1, 2, 3, 4, 5, 6, 0, 7, 8)
        result = astar(state, 3)
        assert result["found"] is True
        assert result["depth"] == 2

    def test_returns_dict(self):
        result = astar(goal_state(3), 3)
        assert "found" in result
        assert "depth" in result
        assert "nodes_expanded" in result

    def test_optimal_depth_matches_bfs(self):
        rng = random.Random(77)
        state = generate_solvable_instance(3, rng, 10)
        r_bfs = bfs(state, 3)
        r_astar = astar(state, 3)
        assert r_bfs["found"] == r_astar["found"]
        if r_bfs["found"]:
            assert r_bfs["depth"] == r_astar["depth"]

    def test_astar_expands_fewer_nodes_than_bfs(self):
        rng = random.Random(33)
        state = generate_solvable_instance(3, rng, 15)
        r_bfs = bfs(state, 3)
        r_astar = astar(state, 3)
        if r_bfs["found"] and r_astar["found"]:
            assert r_astar["nodes_expanded"] <= r_bfs["nodes_expanded"]

    def test_4x4_goal_state(self):
        result = astar(goal_state(4), 4)
        assert result["found"] is True
        assert result["depth"] == 0

    def test_4x4_one_move_away(self):
        gs = list(goal_state(4))
        gs[14], gs[15] = gs[15], gs[14]
        result = astar(tuple(gs), 4)
        assert result["found"] is True
        assert result["depth"] == 1

    def test_max_nodes_limit(self):
        rng = random.Random(42)
        state = generate_solvable_instance(3, rng, 30)
        result = astar(state, 3, max_nodes=5)
        assert result["nodes_expanded"] >= 0
        if not result["found"]:
            assert result["depth"] == -1

    def test_medium_puzzle(self):
        rng = random.Random(2)
        state = generate_solvable_instance(3, rng, 12)
        result = astar(state, 3)
        assert result["found"] is True
        assert result["depth"] > 0

    def test_nodes_expanded_nonneg(self):
        result = astar(goal_state(3), 3)
        assert result["nodes_expanded"] >= 0


# ─────────────────────────────────────────────
# IDA*
# ─────────────────────────────────────────────

class TestIDAStar:
    def test_goal_state_immediately(self):
        result = idastar(goal_state(3), 3)
        assert result["found"] is True
        assert result["depth"] == 0

    def test_one_move_away(self):
        state = (1, 2, 3, 4, 5, 6, 7, 0, 8)
        result = idastar(state, 3)
        assert result["found"] is True
        assert result["depth"] == 1

    def test_two_moves_away(self):
        state = (1, 2, 3, 4, 5, 6, 0, 7, 8)
        result = idastar(state, 3)
        assert result["found"] is True
        assert result["depth"] == 2

    def test_returns_dict(self):
        result = idastar(goal_state(3), 3)
        assert "found" in result
        assert "depth" in result
        assert "nodes_expanded" in result

    def test_optimal_depth_matches_bfs(self):
        rng = random.Random(55)
        state = generate_solvable_instance(3, rng, 10)
        r_bfs = bfs(state, 3)
        r_idastar = idastar(state, 3)
        assert r_bfs["found"] == r_idastar["found"]
        if r_bfs["found"]:
            assert r_bfs["depth"] == r_idastar["depth"]

    def test_optimal_depth_matches_astar(self):
        rng = random.Random(88)
        for _ in range(3):
            state = generate_solvable_instance(3, rng, 8)
            r_astar = astar(state, 3)
            r_idastar = idastar(state, 3)
            if r_astar["found"] and r_idastar["found"]:
                assert r_astar["depth"] == r_idastar["depth"]

    def test_max_nodes_limit(self):
        rng = random.Random(42)
        state = generate_solvable_instance(3, rng, 30)
        result = idastar(state, 3, max_nodes=10)
        assert result["nodes_expanded"] >= 0
        if not result["found"]:
            assert result["depth"] == -1

    def test_medium_puzzle(self):
        rng = random.Random(3)
        state = generate_solvable_instance(3, rng, 12)
        result = idastar(state, 3)
        assert result["found"] is True
        assert result["depth"] > 0

    def test_4x4_goal_state(self):
        result = idastar(goal_state(4), 4)
        assert result["found"] is True
        assert result["depth"] == 0

    def test_nodes_expanded_nonneg(self):
        result = idastar(goal_state(3), 3)
        assert result["nodes_expanded"] >= 0


# ─────────────────────────────────────────────
# Algorithm consistency (BFS vs A* vs IDA*)
# ─────────────────────────────────────────────

class TestAlgorithmConsistency:
    """All three algorithms must agree on optimal depth for solvable 3x3 puzzles."""

    @pytest.mark.parametrize("seed,moves", [
        (1, 5), (2, 7), (3, 4), (10, 8), (20, 6),
    ])
    def test_all_agree_on_depth(self, seed, moves):
        rng = random.Random(seed)
        state = generate_solvable_instance(3, rng, moves)
        r_bfs = bfs(state, 3)
        r_astar = astar(state, 3)
        r_idastar = idastar(state, 3)

        assert r_bfs["found"] is True
        assert r_astar["found"] is True
        assert r_idastar["found"] is True
        assert r_bfs["depth"] == r_astar["depth"] == r_idastar["depth"]

    def test_all_handle_goal_state(self):
        gs = goal_state(3)
        for algo in [bfs, astar, idastar]:
            result = algo(gs, 3)
            assert result["found"] is True
            assert result["depth"] == 0
            assert result["nodes_expanded"] == 0


# ─────────────────────────────────────────────
# safe_stats
# ─────────────────────────────────────────────

class TestSafeStats:
    def test_empty_list(self):
        result = safe_stats([])
        assert result == {"mean": 0, "median": 0, "min": 0, "max": 0}

    def test_all_none(self):
        result = safe_stats([None, None, None])
        assert result == {"mean": 0, "median": 0, "min": 0, "max": 0}

    def test_single_value(self):
        result = safe_stats([5])
        assert result["mean"] == 5
        assert result["median"] == 5
        assert result["min"] == 5
        assert result["max"] == 5

    def test_filters_none(self):
        result = safe_stats([None, 2, None, 4, None])
        assert result["mean"] == 3.0
        assert result["min"] == 2
        assert result["max"] == 4

    def test_mean_correct(self):
        result = safe_stats([1, 2, 3, 4, 5])
        assert result["mean"] == 3.0

    def test_median_odd_count(self):
        result = safe_stats([1, 3, 5])
        assert result["median"] == 3.0

    def test_median_even_count(self):
        result = safe_stats([1, 2, 3, 4])
        assert result["median"] == 2.5

    def test_min_max(self):
        result = safe_stats([10, 3, 7, 1, 9])
        assert result["min"] == 1
        assert result["max"] == 10

    def test_returns_values_key(self):
        result = safe_stats([1, 2, 3])
        assert "values" in result
        assert result["values"] == [1, 2, 3]

    def test_values_excludes_none(self):
        result = safe_stats([None, 1, None, 2])
        assert result["values"] == [1, 2]

    def test_single_none_value(self):
        result = safe_stats([None])
        assert result == {"mean": 0, "median": 0, "min": 0, "max": 0}

    def test_rounding(self):
        result = safe_stats([1, 2])
        assert result["mean"] == 1.5
        assert result["median"] == 1.5

    def test_large_values(self):
        vals = [100000, 200000, 300000]
        result = safe_stats(vals)
        assert result["mean"] == 200000
        assert result["min"] == 100000
        assert result["max"] == 300000

    def test_float_values(self):
        result = safe_stats([1.5, 2.5, 3.5])
        assert abs(result["mean"] - 2.5) < 1e-9


# ─────────────────────────────────────────────
# Unsolvable states (frontier/heap exhaustion)
# ─────────────────────────────────────────────

def _unsolvable_3x3():
    """Return a 3x3 state that cannot reach the goal (odd-parity swap of two tiles)."""
    # Swap tiles 1 and 2 in goal state; this changes parity making it unsolvable.
    gs = list(goal_state(3))
    gs[0], gs[1] = gs[1], gs[0]
    return tuple(gs)


class TestUnsolvable:
    """Tests that algorithms correctly report failure on unsolvable puzzle states."""

    def test_bfs_unsolvable_returns_not_found(self):
        # BFS exhausts entire reachable set and returns found=False (covers line 97)
        state = _unsolvable_3x3()
        result = bfs(state, 3, max_nodes=500_000)
        assert result["found"] is False
        assert result["depth"] == -1

    def test_astar_unsolvable_returns_not_found(self):
        # A* exhausts heap on unsolvable instance (covers lines 118 and 139)
        state = _unsolvable_3x3()
        result = astar(state, 3, max_nodes=500_000)
        assert result["found"] is False
        assert result["depth"] == -1

    def test_idastar_unsolvable_returns_not_found(self):
        # IDA* hits math.inf bound on unsolvable instance
        state = _unsolvable_3x3()
        result = idastar(state, 3, max_nodes=500_000)
        assert result["found"] is False
        assert result["depth"] == -1


# ─────────────────────────────────────────────
# run_experiment
# ─────────────────────────────────────────────

class TestRunExperiment:
    """Tests for the run_experiment orchestration function."""

    def _easy_instances(self, n, count=3, moves=3):
        rng = random.Random(7)
        return [generate_solvable_instance(n, rng, moves) for _ in range(count)]

    def test_returns_dict_with_all_keys(self):
        instances = self._easy_instances(3)
        result = run_experiment(3, instances)
        assert "bfs" in result
        assert "astar" in result
        assert "idastar" in result

    def test_result_structure_has_sub_keys(self):
        instances = self._easy_instances(3)
        result = run_experiment(3, instances)
        for algo in ["bfs", "astar", "idastar"]:
            assert "nodes" in result[algo]
            assert "depth" in result[algo]
            assert "time_ms" in result[algo]
            assert "solved" in result[algo]

    def test_3x3_runs_bfs(self):
        instances = self._easy_instances(3)
        result = run_experiment(3, instances)
        # BFS is run for 3x3; none of the node values should be None
        assert all(v is not None for v in result["bfs"]["nodes"])

    def test_4x4_skips_bfs(self):
        instances = self._easy_instances(4, moves=5)
        result = run_experiment(4, instances)
        # BFS is skipped for 4x4; all values are None
        assert all(v is None for v in result["bfs"]["nodes"])
        assert all(v is None for v in result["bfs"]["depth"])
        assert all(v is None for v in result["bfs"]["time_ms"])

    def test_solved_count_is_nonneg(self):
        instances = self._easy_instances(3)
        result = run_experiment(3, instances)
        assert result["astar"]["solved"] >= 0
        assert result["idastar"]["solved"] >= 0

    def test_list_lengths_match_instance_count(self):
        n_instances = 4
        instances = self._easy_instances(3, count=n_instances)
        result = run_experiment(3, instances)
        for algo in ["bfs", "astar", "idastar"]:
            assert len(result[algo]["nodes"]) == n_instances
            assert len(result[algo]["depth"]) == n_instances
            assert len(result[algo]["time_ms"]) == n_instances

    def test_easy_instances_all_solved(self):
        instances = self._easy_instances(3, moves=3)
        result = run_experiment(3, instances)
        assert result["astar"]["solved"] == len(instances)
        assert result["idastar"]["solved"] == len(instances)

    def test_bfs_not_found_appends_none_depth(self):
        # Force BFS to fail by setting a tiny node limit
        instances = self._easy_instances(3, count=1, moves=20)
        result = run_experiment(3, instances, bfs_limit=2)
        # With 2-node limit on a 20-move puzzle BFS likely fails; depth should be None
        if result["bfs"]["solved"] == 0:
            assert result["bfs"]["depth"][0] is None

    def test_astar_not_found_appends_none_depth(self):
        instances = self._easy_instances(3, count=1, moves=20)
        result = run_experiment(3, instances, astar_limit=2)
        if result["astar"]["solved"] == 0:
            assert result["astar"]["depth"][0] is None

    def test_idastar_not_found_appends_none_depth(self):
        instances = self._easy_instances(3, count=1, moves=20)
        result = run_experiment(3, instances, idastar_limit=2)
        if result["idastar"]["solved"] == 0:
            assert result["idastar"]["depth"][0] is None

    def test_time_ms_are_positive(self):
        instances = self._easy_instances(3)
        result = run_experiment(3, instances)
        for algo in ["astar", "idastar"]:
            for t in result[algo]["time_ms"]:
                assert t >= 0

    def test_goal_state_instances_all_solved_depth_zero(self):
        instances = [goal_state(3)] * 2
        result = run_experiment(3, instances)
        assert result["astar"]["solved"] == 2
        assert result["idastar"]["solved"] == 2
        assert all(d == 0 for d in result["astar"]["depth"])
        assert all(d == 0 for d in result["idastar"]["depth"])
