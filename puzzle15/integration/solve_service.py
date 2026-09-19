"""Threaded solve dispatch for the GUI.

Replaces core/bridge.py's execute_search: same background-thread-plus-
callback shape, but the original's `callback({"success": False, ...});
raise(e)` bug (the re-raise reaches nothing inside a daemon thread - it just
dumps a traceback and kills the thread) is fixed here: log once, call the
callback once, don't re-raise.
"""

from __future__ import annotations

import logging
import threading
from typing import Callable

from puzzle15.solver.board import Board
from puzzle15.solver.registry import run_algorithm
from puzzle15.solver.result import SolveResult

logger = logging.getLogger(__name__)


class SolveService:
    def run_async(
        self,
        algorithm_key: str,
        initial_board: Board,
        goal_board: Board,
        *,
        timeout: float | None,
        max_depth: int = 30,
        on_done: Callable[[SolveResult | None, Exception | None], None],
    ) -> None:
        def run() -> None:
            logger.debug("solve requested: algorithm=%s timeout=%s max_depth=%s", algorithm_key, timeout, max_depth)
            try:
                result = run_algorithm(algorithm_key, initial_board, goal_board, timeout=timeout, max_depth=max_depth)
                logger.debug("solve finished: algorithm=%s success=%s steps=%s explored=%s", algorithm_key, result.success, result.steps, result.explored)
            except Exception as exc:
                logger.exception("solve crashed: algorithm=%s", algorithm_key)
                on_done(None, exc)
                return
            on_done(result, None)

        threading.Thread(target=run, daemon=True).start()
