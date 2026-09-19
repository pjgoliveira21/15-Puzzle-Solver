"""Shuffled-puzzle generation."""

from __future__ import annotations

import copy
import random

from puzzle15.solver.board import Board, get_neighbors, matrix_to_tuple, tuple_to_matrix

DIFFICULTY_MOVES = {"easy": 10, "normal": 35, "hard": 90}
DEFAULT_DIFFICULTY = "easy"


def generate_shuffled_board(difficulty: str, goal_board: Board, rng: random.Random | None = None) -> Board:
    """Shuffle goal_board with random legal moves, avoiding immediate backtracks."""
    rng = rng or random
    n_moves = DIFFICULTY_MOVES.get(difficulty, DIFFICULTY_MOVES[DEFAULT_DIFFICULTY])
    current = copy.deepcopy(goal_board)
    previous_state = None

    for _ in range(n_moves):
        state = matrix_to_tuple(current)
        neighbors = get_neighbors(state)
        valid_neighbors = [n for n in neighbors if n != previous_state]
        if valid_neighbors:
            previous_state = state
            current = tuple_to_matrix(rng.choice(valid_neighbors))

    return current
