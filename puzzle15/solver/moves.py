"""Translate a solved path into plain-language step instructions.

The solver only produces a sequence of boards (`SolveResult.path`); turning
that into "move tile 12 down" is board arithmetic, not GUI/presentation
logic, so it lives here rather than in gui/widgets/panel_steps.py.
"""

from __future__ import annotations

from dataclasses import dataclass

from puzzle15.solver.board import Board, get_empty_position

# Vector a tile itself travels (to_pos - from_pos), not the blank's.
DIRECTION_LABELS: dict[tuple[int, int], str] = {
    (-1, 0): "up",
    (1, 0): "down",
    (0, -1): "left",
    (0, 1): "right",
}


@dataclass(frozen=True)
class MoveInstruction:
    tile: int
    direction: str
    from_pos: tuple[int, int]
    to_pos: tuple[int, int]


def describe_moves(path: list[Board]) -> list[MoveInstruction]:
    """One instruction per consecutive pair of boards in `path`, describing
    which tile moved and which way (the moving tile's own from/to
    position, not the blank's). Raises ValueError if two consecutive
    boards aren't exactly one move apart."""
    instructions: list[MoveInstruction] = []
    for prev, nxt in zip(path, path[1:]):
        prev_blank = get_empty_position(prev)
        next_blank = get_empty_position(nxt)
        if prev_blank is None or next_blank is None:
            raise ValueError("board has no blank tile")

        # The tile that moved now sits where the blank used to be, and came
        # from where the blank is now.
        from_pos, to_pos = next_blank, prev_blank
        vector = (to_pos[0] - from_pos[0], to_pos[1] - from_pos[1])
        direction = DIRECTION_LABELS.get(vector)
        if direction is None:
            raise ValueError(f"boards are not one move apart: {prev} -> {nxt}")

        tile = nxt[to_pos[0]][to_pos[1]]
        instructions.append(MoveInstruction(tile=tile, direction=direction, from_pos=from_pos, to_pos=to_pos))
    return instructions
