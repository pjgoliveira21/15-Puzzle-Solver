"""Digit recognition via template matching against pre-made masks."""

from __future__ import annotations

import logging

import cv2
import numpy as np

from puzzle15.vision.config import DEFAULT_MATCH_THRESHOLD

logger = logging.getLogger(__name__)

GRID_SIZE = 4
MASK_HEIGHT_RATIO = 0.7


def read_numbers(
    numbers_segmented: np.ndarray,
    masks: dict[int, np.ndarray],
    cell_size: int,
    threshold: float = DEFAULT_MATCH_THRESHOLD,
) -> tuple[list[list[int | None]], dict[tuple[int, int], float], dict[tuple[int, int], np.ndarray]]:
    """Recognize the digit in each of the 16 cells via global-best-match
    template matching, largest digit first.

    Returns (grid, scores, cells_processed):
    - grid: 4x4 list of lists, cell value is an int 1-15 or None (blank/unmatched)
    - scores: best TM_CCOEFF_NORMED score per cell that received an assignment
    - cells_processed: binarized image per cell, for debugging/review UI
    """
    if len(numbers_segmented.shape) == 3:
        img_gray = cv2.cvtColor(numbers_segmented, cv2.COLOR_BGR2GRAY)
    else:
        img_gray = numbers_segmented.copy()

    grid: list[list[int | None]] = [[None] * GRID_SIZE for _ in range(GRID_SIZE)]
    scores: dict[tuple[int, int], float] = {}
    occupied_cells: set[tuple[int, int]] = set()

    cells_processed: dict[tuple[int, int], np.ndarray] = {}
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            y1, y2 = i * cell_size, (i + 1) * cell_size
            x1, x2 = j * cell_size, (j + 1) * cell_size
            cell = img_gray[y1:y2, x1:x2]
            _, cell_bin = cv2.threshold(cell, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            cells_processed[(i, j)] = cell_bin

    masks_sorted_names = sorted(masks.keys(), key=int, reverse=True)

    for number in masks_sorted_names:
        mask = masks[number]

        mask_height, mask_width = mask.shape[:2]
        target_mask_height = int(cell_size * MASK_HEIGHT_RATIO)
        scale = target_mask_height / mask_height
        new_mask_width = int(mask_width * scale)

        resized_mask = cv2.resize(mask, (new_mask_width, target_mask_height), interpolation=cv2.INTER_AREA)
        _, mask_bin = cv2.threshold(resized_mask, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        best_match_val = -1.0
        best_cell_coords = None

        for (i, j), cell_bin in cells_processed.items():
            if (i, j) in occupied_cells:
                continue

            res = cv2.matchTemplate(cell_bin, mask_bin, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(res)

            if max_val > best_match_val:
                best_match_val = max_val
                best_cell_coords = (i, j)

        if best_cell_coords and best_match_val >= threshold:
            i, j = best_cell_coords
            grid[i][j] = number
            scores[(i, j)] = best_match_val
            occupied_cells.add((i, j))
            logger.debug("digit %2d -> cell (%d,%d), score=%.3f", number, i, j, best_match_val)
        else:
            logger.debug(
                "digit %2d -> no confident match (best=%.3f at %s, threshold=%.2f)",
                number,
                best_match_val,
                best_cell_coords,
                threshold,
            )

    unmatched_cells = [coords for coords in cells_processed if coords not in occupied_cells]
    logger.debug("recognition done: %d/16 cells matched, unmatched=%s", len(occupied_cells), unmatched_cells)

    return grid, scores, cells_processed
