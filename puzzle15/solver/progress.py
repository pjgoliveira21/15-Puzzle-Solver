"""Throttled progress logging for search algorithms.

A search can explore millions of nodes; logging every node (or every
Nth node) would flood the dev console at a rate that scales with search
speed rather than with how much time the user has been waiting. Logging at
most once per wall-clock interval keeps the log volume roughly proportional
to the timeout instead.
"""

from __future__ import annotations

import logging
import time


class ProgressLogger:
    def __init__(self, logger: logging.Logger, tag: str, start_time: float, interval: float = 1.0):
        self.logger = logger
        self.tag = tag
        self.start_time = start_time
        self.interval = interval
        self._last_log = start_time

    def maybe_log(self, explored: int, **extra: object) -> None:
        now = time.time()
        if now - self._last_log < self.interval:
            return
        self._last_log = now

        elapsed = now - self.start_time
        speed = explored / elapsed if elapsed > 0 else 0
        details = " ".join(f"{key}={value}" for key, value in extra.items())
        self.logger.debug("[%s] explored=%d elapsed=%.1fs speed=%.0f/s %s", self.tag, explored, elapsed, speed, details)
