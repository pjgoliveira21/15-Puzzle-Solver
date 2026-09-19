"""Loading digit template masks used for recognition."""

from __future__ import annotations

import glob
from pathlib import Path

import cv2
import numpy as np

from puzzle15.paths import MASKS_DIR


def load_digit_masks(directory: str | Path = MASKS_DIR, extension: str = "png") -> dict[int, np.ndarray]:
    mask_files = glob.glob(str(Path(directory) / f"*.{extension}"))
    masks: dict[int, np.ndarray] = {}
    for mask_file in mask_files:
        number = int(Path(mask_file).stem.replace("mask", ""))
        masks[number] = cv2.imread(mask_file, cv2.IMREAD_GRAYSCALE)
    return masks
