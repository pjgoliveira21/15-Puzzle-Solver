"""In-memory capture of puzzle15's debug logs, for the GUI's dev console.

The solver/vision packages already call logging.getLogger(__name__).debug(...)
at their key decision points (search start/solved/timeout, etc). This just
gives the GUI a place to read that history back from, without coupling
solver/vision to Tkinter.
"""

from __future__ import annotations

import logging

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_TIME_FORMAT = "%H:%M:%S"


class BufferingLogHandler(logging.Handler):
    """Appends formatted records to a plain, ever-growing list.

    puzzle15 logs a handful of lines per user action (never a per-node
    progress spam), so an unbounded list stays small for the life of a
    desktop session - no ring-buffer bookkeeping needed.
    """

    def __init__(self) -> None:
        super().__init__()
        self.lines: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.lines.append(self.format(record))


def install_debug_log_handler(level: int = logging.DEBUG) -> BufferingLogHandler:
    handler = BufferingLogHandler()
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_TIME_FORMAT))

    logger = logging.getLogger("puzzle15")
    logger.setLevel(level)
    logger.addHandler(handler)
    return handler
