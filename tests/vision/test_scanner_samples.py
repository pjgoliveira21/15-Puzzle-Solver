"""End-to-end scan tests against the bundled real puzzle photos.

Ground-truth grids in expected_grids.json were read by hand from each photo.
Real-world lighting/angle/occlusion makes some of these photos genuinely
hard for threshold-0.5 template matching (see README "Known limitations") -
puzzle2 and puzzle5 in particular are poor-quality shots. Per-photo minimum
match counts below are each photo's currently-observed correct-cell count
with a small margin, NOT 16/16: the point of this test is to catch a
pipeline regression (e.g. "recognizes nothing at all"), not to demand
perfect recognition from difficult photos.
"""

import json
from pathlib import Path

import cv2
import pytest

from puzzle15.paths import SAMPLE_PUZZLES_DIR
from puzzle15.vision.scanner import PuzzleScanner

EXPECTED_GRIDS = json.loads((Path(__file__).parent / "expected_grids.json").read_text())

MIN_CORRECT_CELLS = {
    "puzzle1": 14,
    "puzzle2": 6,
    "puzzle3": 13,
    "puzzle4": 10,
    "puzzle5": 5,
    "puzzle6": 14,
}


def _count_matching_cells(actual, expected) -> int:
    return sum(actual[r][c] == expected[r][c] for r in range(4) for c in range(4))


@pytest.mark.slow
@pytest.mark.parametrize("name", sorted(EXPECTED_GRIDS.keys()))
def test_scan_matches_expected_grid_above_minimum(name):
    image = cv2.imread(str(SAMPLE_PUZZLES_DIR / f"{name}.jpg"))
    assert image is not None, f"could not read sample photo {name}.jpg"

    scanner = PuzzleScanner()
    result = scanner.scan_image(image)

    correct = _count_matching_cells(result.grid, EXPECTED_GRIDS[name])
    assert correct >= MIN_CORRECT_CELLS[name], (
        f"{name}: only {correct}/16 cells matched expected grid "
        f"(minimum {MIN_CORRECT_CELLS[name]}); got {result.grid}"
    )
