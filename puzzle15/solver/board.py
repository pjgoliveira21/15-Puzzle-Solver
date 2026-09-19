"""Board representation and the puzzle's move graph.

A board is a 4x4 grid of ints with -1 marking the blank tile. Matrices
(list of lists) are used at module boundaries; tuples of tuples are used
internally wherever hashability is required (visited sets, heap entries).
"""

from __future__ import annotations

Board = list[list[int]]
BoardTuple = tuple[tuple[int, ...], ...]

BLANK = -1
SIZE = 4

MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def matrix_to_tuple(board: Board) -> BoardTuple:
    return tuple(tuple(row) for row in board)


def tuple_to_matrix(state: BoardTuple) -> Board:
    return [list(row) for row in state]


def get_empty_position(state: BoardTuple | Board) -> tuple[int, int] | None:
    for r in range(SIZE):
        for c in range(SIZE):
            if state[r][c] == BLANK:
                return r, c
    return None


def get_neighbors(state: BoardTuple) -> list[BoardTuple]:
    board = tuple_to_matrix(state)
    pos = get_empty_position(board)
    if pos is None:
        return []

    x, y = pos
    neighbors: list[BoardTuple] = []
    for dx, dy in MOVES:
        nx, ny = x + dx, y + dy
        if 0 <= nx < SIZE and 0 <= ny < SIZE:
            board[x][y], board[nx][ny] = board[nx][ny], board[x][y]
            neighbors.append(matrix_to_tuple(board))
            board[x][y], board[nx][ny] = board[nx][ny], board[x][y]
    return neighbors


def manhattan_distance(state: BoardTuple, goal: BoardTuple) -> int:
    goal_pos = {}
    for r in range(SIZE):
        for c in range(SIZE):
            goal_pos[goal[r][c]] = (r, c)

    distance = 0
    for r in range(SIZE):
        for c in range(SIZE):
            val = state[r][c]
            if val != BLANK:
                target_r, target_c = goal_pos[val]
                distance += abs(r - target_r) + abs(c - target_c)
    return distance
