"""Perspective correction: locate the puzzle frame in a photo and warp it
to a top-down view.

Same contour-scoring/intersection approach as the original Reader project;
the only behavioral change is that failure to locate the puzzle now raises
VisionError instead of the caller receiving an implicit None and crashing
on unpacking.
"""

from __future__ import annotations

import cv2
import numpy as np

from puzzle15.vision.result import VisionError

MIN_CONTOUR_AREA = 1000
MIN_COLOR_FRACTION = 0.01
APPROX_POLY_EPSILON_RATIO = 0.04


def locate_and_warp(
    image: np.ndarray,
    color_config: dict,
    target_size: tuple[int, int] = (800, 800),
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Find the puzzle frame in `image` and return a top-down warp of it.

    Returns (warped, binary_mask, debug_lines_image).
    Raises VisionError if no puzzle contour can be found.
    """
    binary_mask, mask_red, mask_white = _get_segmented_mask(image, color_config)
    vertices, lines_image = _get_vertices(image, binary_mask, mask_red, mask_white)

    if vertices is None:
        raise VisionError("Could not locate the puzzle's frame in the photo.")

    warped = _warp(image, vertices.astype(np.float32), target_size)
    return warped, binary_mask, lines_image


def _get_segmented_mask(img: np.ndarray, color_config: dict) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask_red = cv2.inRange(hsv, color_config["low_red1"], color_config["up_red1"]) | cv2.inRange(
        hsv, color_config["low_red2"], color_config["up_red2"]
    )
    mask_white = cv2.inRange(hsv, color_config["low_white"], color_config["up_white"])
    binary_mask = mask_red | mask_white
    return binary_mask, mask_red, mask_white


def _line_intersection(p1, p2, q1, q2) -> tuple[int, int] | None:
    a1, b1 = p2 - p1
    a2, b2 = q2 - q1

    denom = a1 * b2 - a2 * b1
    if denom == 0:
        return None

    dx = q1[0] - p1[0]
    dy = q1[1] - p1[1]

    t = (dx * b2 - dy * a2) / denom
    x = p1[0] + t * a1
    y = p1[1] + t * b1
    return int(x), int(y)


def _draw_extended_line(img, p1, p2, color, thickness=2) -> None:
    h, w = img.shape[:2]
    p1, p2 = np.array(p1, dtype=np.float32), np.array(p2, dtype=np.float32)
    if p2[0] - p1[0] == 0:
        cv2.line(img, (int(p1[0]), 0), (int(p1[0]), h), color, thickness)
    else:
        m = (p2[1] - p1[1]) / (p2[0] - p1[0])
        b = p1[1] - m * p1[0]
        cv2.line(img, (0, int(b)), (w, int(m * w + b)), color, thickness)


def _get_vertices(image, binary_mask, mask_red, mask_white):
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    img_h, img_w = binary_mask.shape[:2]
    best_contour = None
    best_score = -1

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < MIN_CONTOUR_AREA:
            continue

        contour_mask = np.zeros((img_h, img_w), dtype=np.uint8)
        cv2.drawContours(contour_mask, [contour], -1, 255, -1)
        red_pixels = cv2.countNonZero(cv2.bitwise_and(mask_red, mask_red, mask=contour_mask))
        white_pixels = cv2.countNonZero(cv2.bitwise_and(mask_white, mask_white, mask=contour_mask))

        if red_pixels < MIN_COLOR_FRACTION * area or white_pixels < MIN_COLOR_FRACTION * area:
            continue

        score = (area / (img_h * img_w)) * ((red_pixels + white_pixels) / area)
        if score > best_score:
            best_score = score
            best_contour = contour

    if best_contour is None:
        return None, None

    perimeter = cv2.arcLength(best_contour, True)
    approx_vertices = cv2.approxPolyDP(best_contour, APPROX_POLY_EPSILON_RATIO * perimeter, True)

    lines = []
    n = len(approx_vertices)
    for i in range(n):
        p1 = approx_vertices[i][0].astype(float)
        p2 = approx_vertices[(i + 1) % n][0].astype(float)
        length = np.linalg.norm(p2 - p1)
        lines.append({"p1": p1, "p2": p2, "len": length})

    sorted_lines = sorted(lines, key=lambda x: x["len"], reverse=True)[:4]
    intersections = []
    for i in range(len(sorted_lines)):
        for j in range(i + 1, len(sorted_lines)):
            point = _line_intersection(sorted_lines[i]["p1"], sorted_lines[i]["p2"], sorted_lines[j]["p1"], sorted_lines[j]["p2"])
            if point:
                intersections.append(point)

    moments = cv2.moments(binary_mask)
    cx, cy = int(moments["m10"] / moments["m00"]), int(moments["m01"] / moments["m00"])
    intersections = sorted(intersections, key=lambda pt: np.linalg.norm(np.array(pt) - [cx, cy]))
    vertices = order_vertices(np.array(intersections[:4], dtype=np.float32))

    lines_image = image.copy()
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]
    for i in range(4):
        _draw_extended_line(lines_image, sorted_lines[i]["p1"], sorted_lines[i]["p2"], colors[i], 2)
        cv2.circle(lines_image, (int(vertices[i][0]), int(vertices[i][1])), 20, colors[i], -1)

    return vertices, lines_image


def order_vertices(vertices: np.ndarray) -> np.ndarray:
    """Order 4 points as top-left, top-right, bottom-right, bottom-left."""
    s = vertices.sum(axis=1)
    diff = np.diff(vertices, axis=1).flatten()
    ordered = np.zeros((4, 2), dtype=np.float32)
    ordered[0] = vertices[np.argmin(s)]
    ordered[2] = vertices[np.argmax(s)]
    ordered[1] = vertices[np.argmin(diff)]
    ordered[3] = vertices[np.argmax(diff)]
    return ordered


def _warp(img: np.ndarray, vertices: np.ndarray, target_size: tuple[int, int]) -> np.ndarray:
    w, h = target_size
    dst_points = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float32)
    transformation_matrix = cv2.getPerspectiveTransform(vertices, dst_points)
    return cv2.warpPerspective(img, transformation_matrix, (w, h))
