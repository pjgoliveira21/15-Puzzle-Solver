"""Standalone CLI to run the scan pipeline against a bundled sample photo
and show the debug plots, mirroring the original Reader project's main.py.

Usage: python -m puzzle15.vision.debug_cli [puzzle1]
"""

import argparse

import cv2

from puzzle15.paths import SAMPLE_PUZZLES_DIR
from puzzle15.vision.debug_plots import show_scan_debug_plots
from puzzle15.vision.result import VisionError
from puzzle15.vision.scanner import PuzzleScanner


def main() -> None:
    parser = argparse.ArgumentParser(description="Digitalize a photo of a 15-puzzle to a 4x4 grid")
    parser.add_argument("file", nargs="?", default="puzzle1", help="Sample file name under assets/sample_puzzles (no extension)")
    args = parser.parse_args()

    image_path = SAMPLE_PUZZLES_DIR / f"{args.file}.jpg"
    original = cv2.imread(str(image_path))
    if original is None:
        raise SystemExit(f"Could not read image file: {image_path}")

    scanner = PuzzleScanner()
    try:
        result = scanner.scan_image(original)
    except VisionError as exc:
        raise SystemExit(str(exc)) from exc

    for row in result.grid:
        print(row)

    cell_size = scanner.target_size[0] // 4
    show_scan_debug_plots(
        original,
        result.binary_mask,
        result.warped,
        result.lines_image,
        result.numbers_segmented,
        scanner.target_size,
        cell_size,
        result.cells_processed,
        result.grid,
    )


if __name__ == "__main__":
    main()
