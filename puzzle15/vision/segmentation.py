"""Isolating the digit-bearing region of a warped puzzle image.

Extracted from the original Reader project's main.py script body (it lived
inline at module scope, making it untestable) - same HSV bounds and
morphological close kernel.
"""

import cv2
import numpy as np

CLOSE_KERNEL = np.ones((9, 9), np.uint8)


def segment_numbers_region(warped: np.ndarray, color_config: dict) -> np.ndarray:
    """Return `warped` with the red/white frame removed, leaving digits."""
    hsv = cv2.cvtColor(warped, cv2.COLOR_BGR2HSV)

    mask_red1 = cv2.inRange(hsv, color_config["low_red1"], color_config["up_red1"])
    mask_red2 = cv2.inRange(hsv, color_config["low_red2"], color_config["up_red2"])
    mask_white = cv2.inRange(hsv, color_config["low_white"], color_config["up_white"])
    mask_red = cv2.bitwise_or(mask_red1, mask_red2)

    mask_not_red_white = cv2.bitwise_not(cv2.bitwise_or(mask_red, mask_white))
    numbers_segmented = cv2.bitwise_and(warped, warped, mask=mask_not_red_white)
    numbers_segmented = cv2.morphologyEx(numbers_segmented, cv2.MORPH_CLOSE, CLOSE_KERNEL)
    return numbers_segmented
