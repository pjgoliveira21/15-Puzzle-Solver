import pytest

from puzzle15.solver.moves import MoveInstruction, describe_moves
from puzzle15.solver.registry import run_algorithm

GOAL = [
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12],
    [13, 14, 15, -1],
]

# One move away from GOAL (blank swapped with 15) - same fixture as
# test_algorithms.py.
ONE_MOVE_AWAY = [
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12],
    [13, 14, -1, 15],
]


def test_empty_path_has_no_moves():
    assert describe_moves([GOAL]) == []


def test_single_horizontal_move():
    # Blank at (3,2) -> (3,3): tile 15 moves left from (3,3) to (3,2).
    instructions = describe_moves([ONE_MOVE_AWAY, GOAL])
    assert instructions == [MoveInstruction(tile=15, direction="left", from_pos=(3, 3), to_pos=(3, 2))]


def test_single_vertical_move():
    prev = [
        [1, 2, 3, 4],
        [5, 6, 7, -1],
        [9, 10, 11, 8],
        [13, 14, 15, 12],
    ]
    nxt = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, -1],
        [13, 14, 15, 12],
    ]
    # Blank at (1,3) -> (2,3): tile 8 (at (2,3) in prev) moves up into the
    # blank's old spot, from (2,3) to (1,3).
    instructions = describe_moves([prev, nxt])
    assert instructions == [MoveInstruction(tile=8, direction="up", from_pos=(2, 3), to_pos=(1, 3))]


def test_round_trip_replays_solved_path():
    result = run_algorithm("astar", ONE_MOVE_AWAY, GOAL, timeout=10)
    instructions = describe_moves(result.path)
    assert len(instructions) == result.steps

    board = [row[:] for row in result.path[0]]
    for i, move in enumerate(instructions):
        board[move.from_pos[0]][move.from_pos[1]], board[move.to_pos[0]][move.to_pos[1]] = (
            board[move.to_pos[0]][move.to_pos[1]],
            board[move.from_pos[0]][move.from_pos[1]],
        )
        assert board == result.path[i + 1]


def test_non_adjacent_boards_raise_value_error():
    other = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
        [13, -1, 14, 15],
    ]
    with pytest.raises(ValueError):
        describe_moves([GOAL, other])
