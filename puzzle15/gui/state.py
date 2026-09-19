from __future__ import annotations

from dataclasses import dataclass

from puzzle15.solver.board import Board


@dataclass
class AppState:
    initial_board: Board | None = None
    goal_board: Board | None = None
