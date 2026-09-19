import pytest

from puzzle15.integration.board_conversion import (
    BoardValidationError,
    scan_grid_to_board,
    validate_board,
)

VALID_GRID = [
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12],
    [13, 14, 15, None],
]

VALID_BOARD = [
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12],
    [13, 14, 15, -1],
]


def test_scan_grid_to_board_converts_none_to_blank():
    assert scan_grid_to_board(VALID_GRID) == VALID_BOARD


def test_scan_grid_to_board_rejects_zero_blanks():
    grid = [row[:] for row in VALID_GRID]
    grid[3][3] = 15  # duplicate 15, no blank left
    with pytest.raises(BoardValidationError):
        scan_grid_to_board(grid)


def test_scan_grid_to_board_rejects_multiple_blanks():
    grid = [row[:] for row in VALID_GRID]
    grid[0][0] = None
    with pytest.raises(BoardValidationError):
        scan_grid_to_board(grid)


def test_validate_board_accepts_valid_board():
    validate_board(VALID_BOARD)  # should not raise


def test_validate_board_rejects_wrong_shape():
    with pytest.raises(BoardValidationError):
        validate_board([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]])


def test_validate_board_rejects_no_blank():
    board = [row[:] for row in VALID_BOARD]
    board[3][3] = 1  # duplicate, no blank
    with pytest.raises(BoardValidationError):
        validate_board(board)


def test_validate_board_rejects_duplicate_value():
    board = [row[:] for row in VALID_BOARD]
    board[0][0] = 2  # duplicate of [0][1], and 1 is now missing
    with pytest.raises(BoardValidationError) as exc_info:
        validate_board(board)
    assert (0, 0) in exc_info.value.cell_errors
    assert (0, 1) in exc_info.value.cell_errors


def test_validate_board_rejects_out_of_range_value():
    board = [row[:] for row in VALID_BOARD]
    board[0][0] = 99
    with pytest.raises(BoardValidationError) as exc_info:
        validate_board(board)
    assert (0, 0) in exc_info.value.cell_errors
