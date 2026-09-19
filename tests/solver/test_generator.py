import random

from puzzle15.solver.generator import generate_shuffled_board

GOAL = [
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12],
    [13, 14, 15, -1],
]


def test_shuffled_board_is_valid_permutation():
    board = generate_shuffled_board("hard", GOAL, rng=random.Random(42))
    values = sorted(v for row in board for v in row)
    assert values == sorted(v for row in GOAL for v in row)


def test_shuffled_board_is_deterministic_with_seed():
    a = generate_shuffled_board("normal", GOAL, rng=random.Random(7))
    b = generate_shuffled_board("normal", GOAL, rng=random.Random(7))
    assert a == b


def test_unknown_difficulty_falls_back_to_default():
    board = generate_shuffled_board("nonexistent", GOAL, rng=random.Random(1))
    values = sorted(v for row in board for v in row)
    assert values == sorted(v for row in GOAL for v in row)
