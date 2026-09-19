"""Default HSV segmentation bounds for the red/white 15-puzzle frame."""

import numpy as np

DEFAULT_COLOR_CONFIG = {
    "low_red1": np.array([0, 80, 60]),
    "up_red1": np.array([10, 255, 255]),
    "low_red2": np.array([170, 80, 60]),
    "up_red2": np.array([180, 255, 255]),
    "low_white": np.array([0, 0, 170]),
    "up_white": np.array([180, 80, 255]),
}

DEFAULT_TARGET_SIZE = (800, 800)
DEFAULT_MATCH_THRESHOLD = 0.5
