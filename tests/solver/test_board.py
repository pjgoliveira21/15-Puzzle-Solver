from puzzle15.solver.board import (
    get_empty_position,
    get_neighbors,
    manhattan_distance,
    matrix_to_tuple,
    tuple_to_matrix,
)

GOAL = [
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12],
    [13, 14, 15, -1],
]


def test_matrix_tuple_roundtrip():
    state = matrix_to_tuple(GOAL)
    assert tuple_to_matrix(state) == GOAL


def test_get_empty_position_corner():
    assert get_empty_position(GOAL) == (3, 3)


def test_get_empty_position_not_found():
    board = [[1] * 4 for _ in range(4)]
    assert get_empty_position(board) is None


def test_get_neighbors_corner_has_two_moves():
    state = matrix_to_tuple(GOAL)
    assert len(get_neighbors(state)) == 2


def test_get_neighbors_center_has_four_moves():
    board = [
        [1, 2, 3, 4],
        [5, 6, -1, 8],
        [9, 10, 11, 12],
        [13, 14, 15, 7],
    ]
    state = matrix_to_tuple(board)
    assert len(get_neighbors(state)) == 4


def test_get_neighbors_edge_has_three_moves():
    board = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
        [13, -1, 15, 14],
    ]
    state = matrix_to_tuple(board)
    assert len(get_neighbors(state)) == 3


def test_manhattan_distance_zero_at_goal():
    goal = matrix_to_tuple(GOAL)
    assert manhattan_distance(goal, goal) == 0


def test_manhattan_distance_known_value():
    board = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
        [13, 14, -1, 15],
    ]
    goal = matrix_to_tuple(GOAL)
    state = matrix_to_tuple(board)
    # Only tile 15 is displaced, by one step; the blank isn't counted.
    assert manhattan_distance(state, goal) == 1
