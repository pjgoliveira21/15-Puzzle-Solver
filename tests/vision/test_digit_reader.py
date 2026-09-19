import cv2
import numpy as np

from puzzle15.vision.digit_reader import read_numbers
from puzzle15.vision.masks import load_digit_masks

CELL_SIZE = 100
GRID_PIXELS = CELL_SIZE * 4

GOAL_GRID = [
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12],
    [13, 14, 15, None],
]


def _paste_mask_in_cell(canvas, mask, row, col):
    target_height = int(CELL_SIZE * 0.7)
    scale = target_height / mask.shape[0]
    resized = cv2.resize(mask, (int(mask.shape[1] * scale), target_height))

    y0 = row * CELL_SIZE + (CELL_SIZE - resized.shape[0]) // 2
    x0 = col * CELL_SIZE + (CELL_SIZE - resized.shape[1]) // 2
    canvas[y0 : y0 + resized.shape[0], x0 : x0 + resized.shape[1]] = resized
    return canvas


def _make_canvas(masks, grid):
    # A perfectly uniform (all-zero) background makes Otsu thresholding on
    # empty cells degenerate (no real bimodal split); real segmented photos
    # are never that uniform, so a little background noise keeps this
    # representative - matches the never-fully-empty backgrounds a real scan
    # segments (frame remnants, warp artifacts).
    rng = np.random.default_rng(0)
    canvas = rng.integers(20, 60, size=(GRID_PIXELS, GRID_PIXELS), dtype=np.uint8)
    for row in range(4):
        for col in range(4):
            value = grid[row][col]
            if value is not None:
                canvas = _paste_mask_in_cell(canvas, masks[value], row, col)
    return canvas


def test_recognizes_a_single_pasted_digit_against_noise():
    masks = load_digit_masks()
    canvas = _make_canvas(masks, [[None] * 4 for _ in range(4)])
    canvas = _paste_mask_in_cell(canvas, masks[7], row=2, col=1)

    grid, scores, _ = read_numbers(canvas, masks, cell_size=CELL_SIZE)

    assert grid[2][1] == 7
    assert (2, 1) in scores


def test_recognizes_a_full_valid_grid():
    # Every digit competing for its own cell at once (the shape of a real
    # scan) is a fairer test of the global-best-match algorithm than a
    # couple of digits surrounded by mostly-empty cells: with few real
    # digits present, noise cells can spuriously out-score them for a
    # mask before its rightful cell is reached (masks are tried in
    # descending order, and a claimed cell is removed from competition).
    masks = load_digit_masks()
    canvas = _make_canvas(masks, GOAL_GRID)

    grid, scores, _ = read_numbers(canvas, masks, cell_size=CELL_SIZE)

    assert grid == GOAL_GRID
    assert len(scores) == 15
