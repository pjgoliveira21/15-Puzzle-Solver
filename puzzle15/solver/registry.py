"""Registry of solvable algorithms, keyed by a stable, language-neutral id.

The GUI's display labels live here as the `label` field so the rest of the
solver package never needs to know what language the UI is in.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from puzzle15.solver.algorithms.astar import solve_astar
from puzzle15.solver.algorithms.bfs import solve_bfs
from puzzle15.solver.algorithms.dfs import solve_dfs
from puzzle15.solver.algorithms.gbfs import solve_gbfs
from puzzle15.solver.algorithms.idastar import solve_idastar
from puzzle15.solver.board import Board
from puzzle15.solver.result import SolveResult


@dataclass(frozen=True)
class AlgorithmSpec:
    key: str
    label: str
    solve: Callable[..., SolveResult]
    supports_max_depth: bool = False


# Shared with the GUI (algorithm settings dialog, Easy mode's auto-solve,
# the algorithm-comparison dialog) so there's one source of truth instead
# of each caller picking its own default.
DEFAULT_TIMEOUT = 30
DEFAULT_MAX_DEPTH = 30


ALGORITHMS: dict[str, AlgorithmSpec] = {
    "dfs": AlgorithmSpec("dfs", "Depth-First Search", solve_dfs, supports_max_depth=True),
    "bfs": AlgorithmSpec("bfs", "Breadth-First Search", solve_bfs),
    "gbfs": AlgorithmSpec("gbfs", "Greedy Best-First Search", solve_gbfs),
    "astar": AlgorithmSpec("astar", "A*", solve_astar),
    "idastar": AlgorithmSpec("idastar", "Iterative Deepening A*", solve_idastar),
}


def run_algorithm(
    algorithm_key: str,
    initial_board: Board,
    goal_board: Board,
    *,
    timeout: float | None = None,
    max_depth: int = 30,
) -> SolveResult:
    spec = ALGORITHMS[algorithm_key]
    if spec.supports_max_depth:
        return spec.solve(initial_board, goal_board, max_depth, timeout)
    return spec.solve(initial_board, goal_board, timeout)


def run_all_algorithms(
    initial_board: Board,
    goal_board: Board,
    *,
    timeout: float | None = None,
) -> dict[str, SolveResult]:
    """Run every registered algorithm against the same board, sequentially
    (not in parallel - the point is a fair timing comparison)."""
    return {key: run_algorithm(key, initial_board, goal_board, timeout=timeout) for key in ALGORITHMS}
