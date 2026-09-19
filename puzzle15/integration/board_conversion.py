"""The -1 <-> None boundary between vision output and solver input.

Vision's `None` means "no digit matched confidently" - a distinct concept
from the solver's `-1` blank-tile sentinel. They're deliberately kept apart
until the user explicitly accepts a scan (see gui/dialogs/scan_review_dialog.py),
so a merely-unmatched cell is never silently treated as the puzzle's blank.
"""

from __future__ import annotations

from puzzle15.solver.board import BLANK, SIZE, Board

EXPECTED_VALUES = set(range(1, 16))


class BoardValidationError(Exception):
    def __init__(self, message: str, cell_errors: dict[tuple[int, int], str] | None = None):
        super().__init__(message)
        self.message = message
        self.cell_errors = cell_errors or {}


def scan_grid_to_board(grid: list[list[int | None]]) -> Board:
    """Convert a vision-native grid (None = blank/unmatched) to a Board (-1 = blank).

    Raises BoardValidationError if `grid` doesn't have exactly one None cell -
    at that point there's no unambiguous way to decide which one is the blank.
    """
    none_count = sum(1 for row in grid for value in row if value is None)
    if none_count != 1:
        raise BoardValidationError(
            f"Expected exactly one blank cell, found {none_count}. "
            "Correct any misread cells so exactly one is marked blank."
        )
    return [[BLANK if value is None else value for value in row] for row in grid]


def validate_board(board: Board) -> None:
    """Raise BoardValidationError unless board is 4x4 with exactly one -1
    and values 1-15 each appearing exactly once."""
    if len(board) != SIZE or any(len(row) != SIZE for row in board):
        raise BoardValidationError(f"Board must be {SIZE}x{SIZE}.")

    cell_errors: dict[tuple[int, int], str] = {}
    seen: dict[int, tuple[int, int]] = {}
    blank_count = 0

    for r, row in enumerate(board):
        for c, value in enumerate(row):
            if value == BLANK:
                blank_count += 1
                continue
            if value not in EXPECTED_VALUES:
                cell_errors[(r, c)] = f"{value} is not a valid tile value (expected 1-15 or blank)."
            elif value in seen:
                cell_errors[(r, c)] = f"{value} appears more than once."
                cell_errors[seen[value]] = f"{value} appears more than once."
            else:
                seen[value] = (r, c)

    if blank_count != 1:
        raise BoardValidationError(f"Board must have exactly one blank cell, found {blank_count}.", cell_errors)

    missing = EXPECTED_VALUES - seen.keys()
    if missing or cell_errors:
        missing_text = f" Missing: {sorted(missing)}." if missing else ""
        raise BoardValidationError(f"Board is not a valid permutation of 1-15 plus one blank.{missing_text}", cell_errors)
