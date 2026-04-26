"""
CS 57200 - Heuristic Problem Solving
Phase 3 Ablation Study: Manhattan vs Linear Conflict vs Disjoint PDB.

This script runs A* and IDA* on a fixed set of 4x4 (15-puzzle) instances
across three admissible heuristics and saves results to JSON for chart
generation. It also includes a 3x3 (8-puzzle) PDB study for completeness.

Outputs:
    ablation_results.json
        {
          "seed": 1234,
          "n": 4,
          "scramble_depth": ...,
          "n_instances": ...,
          "heuristics": {
              "manhattan":     {astar: [...], idastar: [...]},
              "linear":        {astar: [...], idastar: [...]},
              "pdb_4_4_4_3":   {astar: [...], idastar: [...]}
          },
          "pdb_build_seconds": ...
        }

Reproducibility:
    seed=1234 used throughout; 50 instances at scramble depth 30 by default.
"""

import argparse
import json
import os
import random
import sys
import time
from typing import Callable, Dict, List, Tuple

from heuristics import (
    GROUPS_4_4_4_3,
    GROUPS_4_4_8PUZZLE,
    build_pdb,
    linear_conflict,
    manhattan_distance,
    pdb_lookup,
)
from solver import astar, idastar, generate_solvable_instance


def time_call(fn, *args, **kwargs) -> Tuple[float, Dict]:
    """Time a single algorithm call. Returns (ms, result_dict)."""
    t0 = time.perf_counter()
    r = fn(*args, **kwargs)
    return (time.perf_counter() - t0) * 1000.0, r


def run_one(alg: Callable, instance: Tuple[int, ...], n: int,
            heuristic: Callable, max_nodes: int) -> Dict:
    """
    Run a single algorithm on a single instance with the given heuristic.

    Args:
        alg: ``astar`` or ``idastar``.
        instance: state tuple.
        n: board side length.
        heuristic: ``h(state, n) -> int``.
        max_nodes: hard cap for the search.

    Returns:
        Dict with ``nodes``, ``depth``, ``time_ms``, ``solved`` keys.
    """
    ms, r = time_call(alg, instance, n, heuristic=heuristic,
                      max_nodes=max_nodes)
    return {
        "nodes": r["nodes_expanded"],
        "depth": r["depth"] if r["found"] else None,
        "time_ms": ms,
        "solved": bool(r["found"]),
    }


def make_pdb_heuristic_callable(pdbs, groups):
    """
    Wrap PDB lookup into the (state, n) -> int interface used by solver.

    The ``n`` parameter is ignored because the partition fixes the size.
    """
    def h(state, _n):
        return pdb_lookup(state, pdbs, groups)
    return h


def main(argv=None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Phase 3 ablation: heuristic comparison for the "
                    "15-puzzle (and optional 8-puzzle PDB study).")
    parser.add_argument("--n", type=int, default=4, choices=(3, 4),
                        help="Board side length (3 or 4).")
    parser.add_argument("--scramble", type=int, default=30,
                        help="Scramble depth from goal.")
    parser.add_argument("--instances", type=int, default=50,
                        help="Number of random solvable instances.")
    parser.add_argument("--seed", type=int, default=1234,
                        help="RNG seed for instance generation.")
    parser.add_argument("--max-nodes", type=int, default=2_000_000,
                        help="Per-search node cap.")
    parser.add_argument("--out", type=str, default="ablation_results.json",
                        help="Output JSON path.")
    parser.add_argument("--include-bfs", action="store_true",
                        help="Also run uninformed BFS (3x3 only).")
    args = parser.parse_args(argv)

    n = args.n
    rng = random.Random(args.seed)

    print(f"=== Phase 3 ablation: n={n}, scramble={args.scramble}, "
          f"instances={args.instances}, seed={args.seed} ===")

    # ── Build PDBs ──
    if n == 4:
        groups = GROUPS_4_4_4_3
    else:
        groups = GROUPS_4_4_8PUZZLE
    print(f"Building disjoint PDBs for partition {groups}...")
    t0 = time.time()
    pdbs = [build_pdb(g, n=n) for g in groups]
    pdb_build_s = time.time() - t0
    print(f"  Built {len(pdbs)} PDBs in {pdb_build_s:.2f}s "
          f"(total entries: {sum(len(p) for p in pdbs):,})")

    pdb_h = make_pdb_heuristic_callable(pdbs, groups)

    # ── Generate instances ──
    print(f"Generating {args.instances} solvable instances...")
    instances = [generate_solvable_instance(n, rng, args.scramble)
                 for _ in range(args.instances)]

    # ── Heuristic suite ──
    heur_suite = {
        "manhattan":  manhattan_distance,
        "linear":     linear_conflict,
        "pdb":        pdb_h,
    }

    results: Dict = {
        "seed": args.seed,
        "n": n,
        "scramble_depth": args.scramble,
        "n_instances": args.instances,
        "max_nodes": args.max_nodes,
        "pdb_build_seconds": pdb_build_s,
        "pdb_partition": [list(g) for g in groups],
        "heuristics": {h: {"astar": [], "idastar": []} for h in heur_suite},
    }

    # ── Run experiments ──
    for hname, hfunc in heur_suite.items():
        print(f"\n--- Heuristic: {hname} ---")
        for i, inst in enumerate(instances):
            print(f"  Instance {i+1}/{args.instances}", end="\r", flush=True)
            r_a = run_one(astar, inst, n, hfunc, args.max_nodes)
            r_i = run_one(idastar, inst, n, hfunc, args.max_nodes)
            results["heuristics"][hname]["astar"].append(r_a)
            results["heuristics"][hname]["idastar"].append(r_i)
        a_solved = sum(1 for r in results["heuristics"][hname]["astar"]
                       if r["solved"])
        i_solved = sum(1 for r in results["heuristics"][hname]["idastar"]
                       if r["solved"])
        print(f"\n  A* solved {a_solved}/{args.instances}, "
              f"IDA* solved {i_solved}/{args.instances}")

    with open(args.out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults written to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
