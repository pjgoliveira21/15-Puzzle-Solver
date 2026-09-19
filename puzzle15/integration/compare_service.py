"""Threaded "compare all algorithms" dispatch for the GUI.

Mirrors SolveService/ScanService's background-thread-plus-callback shape,
wrapping the synchronous, pure `run_all_algorithms` so Advanced mode's
Compare Algorithms action doesn't freeze the UI while all five searches run.
"""

from __future__ import annotations

import logging
import threading
from typing import Callable

from puzzle15.solver.board import Board
from puzzle15.solver.registry import run_all_algorithms
from puzzle15.solver.result import SolveResult

logger = logging.getLogger(__name__)


class CompareService:
    def run_all_async(
        self,
        initial_board: Board,
        goal_board: Board,
        *,
        timeout: float | None,
        on_done: Callable[[dict[str, SolveResult] | None, Exception | None], None],
    ) -> None:
        def run() -> None:
            logger.debug("compare requested: timeout=%s", timeout)
            try:
                results = run_all_algorithms(initial_board, goal_board, timeout=timeout)
                logger.debug("compare finished: %s", {key: result.success for key, result in results.items()})
            except Exception as exc:
                logger.exception("compare crashed")
                on_done(None, exc)
                return
            on_done(results, None)

        threading.Thread(target=run, daemon=True).start()
