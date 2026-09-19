"""PuzzleScanner - the single entry point for turning a photo into a grid."""

from __future__ import annotations

import logging
import time
from pathlib import Path

import cv2
import numpy as np

from puzzle15.vision.config import DEFAULT_COLOR_CONFIG, DEFAULT_MATCH_THRESHOLD, DEFAULT_TARGET_SIZE
from puzzle15.vision.digit_reader import read_numbers
from puzzle15.vision.masks import load_digit_masks
from puzzle15.vision.perspective import locate_and_warp
from puzzle15.vision.result import ScanResult, VisionError
from puzzle15.vision.segmentation import segment_numbers_region

logger = logging.getLogger(__name__)


class PuzzleScanner:
    def __init__(
        self,
        masks: dict[int, np.ndarray] | None = None,
        color_config: dict = DEFAULT_COLOR_CONFIG,
        target_size: tuple[int, int] = DEFAULT_TARGET_SIZE,
        threshold: float = DEFAULT_MATCH_THRESHOLD,
    ):
        self.masks = masks if masks is not None else load_digit_masks()
        self.color_config = color_config
        self.target_size = target_size
        self.threshold = threshold

    def scan_file(self, path: str | Path) -> ScanResult:
        logger.debug("scan_file: %s", path)
        image = cv2.imread(str(path))
        if image is None:
            raise VisionError(f"Could not read image file: {path}")
        return self.scan_image(image)

    def scan_image(self, image: np.ndarray) -> ScanResult:
        start_time = time.time()
        logger.debug("scan starting: image_shape=%s target_size=%s threshold=%.2f", image.shape, self.target_size, self.threshold)

        warped, binary_mask, lines_image = locate_and_warp(image, self.color_config, self.target_size)
        logger.debug("puzzle frame located and warped to %s", self.target_size)

        numbers_segmented = segment_numbers_region(warped, self.color_config)

        cell_size = self.target_size[0] // 4
        grid, scores, cells_processed = read_numbers(numbers_segmented, self.masks, cell_size, self.threshold)

        matched = sum(1 for row in grid for value in row if value is not None)
        avg_score = sum(scores.values()) / len(scores) if scores else 0.0
        elapsed = time.time() - start_time
        logger.debug(
            "scan complete: time=%.2fs matched=%d/16 unmatched=%d avg_confidence=%.3f",
            elapsed,
            matched,
            16 - matched,
            avg_score,
        )

        return ScanResult(
            grid=grid,
            scores=scores,
            warped=warped,
            binary_mask=binary_mask,
            lines_image=lines_image,
            numbers_segmented=numbers_segmented,
            cells_processed=cells_processed,
        )
