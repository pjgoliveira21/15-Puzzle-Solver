"""Search result type shared by every algorithm."""

from __future__ import annotations

import time
from dataclasses import dataclass

from puzzle15.solver.board import Board, BoardTuple, tuple_to_matrix


class SearchTimeout(Exception):
    """Raised internally when a search exceeds its allotted time."""


@dataclass
class SolveResult:
    success: bool
    time_seconds: float
    explored: int
    steps: int
    path: list[Board] | None


def make_result(
    success: bool,
    start_time: float,
    explored: int,
    path_tuples: list[BoardTuple] | None = None,
) -> SolveResult:
    elapsed = time.time() - start_time
    path = [tuple_to_matrix(state) for state in path_tuples] if path_tuples else None
    steps = len(path_tuples) - 1 if path_tuples else 0
    return SolveResult(
        success=success,
        time_seconds=round(elapsed, 3),
        explored=explored,
        steps=steps,
        path=path,
    )
