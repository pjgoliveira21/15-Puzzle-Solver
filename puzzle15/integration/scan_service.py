"""Threaded scan dispatch for the GUI.

A scan does a perspective warp plus up to 15x16 template-match calls -
enough to visibly stutter the UI if run on the main thread - so this
mirrors SolveService's background-thread-plus-callback shape.
"""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Callable

from puzzle15.vision.result import ScanResult, VisionError
from puzzle15.vision.scanner import PuzzleScanner

logger = logging.getLogger(__name__)


class ScanService:
    def __init__(self, scanner: PuzzleScanner | None = None):
        self.scanner = scanner or PuzzleScanner()

    def scan_file_async(
        self,
        path: str | Path,
        *,
        on_done: Callable[[ScanResult], None],
        on_error: Callable[[Exception], None],
    ) -> None:
        def run() -> None:
            logger.debug("scan requested: %s", path)
            try:
                result = self.scanner.scan_file(path)
                on_done(result)
            except VisionError as exc:
                logger.debug("scan rejected: %s", exc)
                on_error(exc)
            except Exception as exc:
                logger.exception("scan crashed for %s", path)
                on_error(exc)

        threading.Thread(target=run, daemon=True).start()
