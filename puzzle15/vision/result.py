"""Types shared across the vision package."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


class VisionError(Exception):
    """Raised when a photo can't be turned into a puzzle grid."""


@dataclass
class ScanResult:
    grid: list[list[int | None]]  # 4x4, None = no digit matched confidently
    scores: dict[tuple[int, int], float]  # best template-match score per assigned cell
    warped: np.ndarray
    binary_mask: np.ndarray
    lines_image: np.ndarray
    numbers_segmented: np.ndarray
    cells_processed: dict[tuple[int, int], np.ndarray]
