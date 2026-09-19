"""Loading goal-state presets and arbitrary board JSON files."""

from __future__ import annotations

import json
from pathlib import Path

from puzzle15.paths import GOAL_STATES_PATH
from puzzle15.solver.board import Board

PRESET_KEYS = ("row_asc", "row_desc", "col_asc", "col_desc")
DEFAULT_PRESET = "row_asc"


def load_goal_states() -> dict:
    with open(GOAL_STATES_PATH) as f:
        return json.load(f)


def get_goal_state(key: str) -> Board:
    """Look up a preset goal board by key.

    Numeric presets (row_asc/row_desc/col_asc/col_desc) and colored presets
    share one namespace; unknown keys fall back to DEFAULT_PRESET.
    """
    states = load_goal_states()
    if key in PRESET_KEYS:
        return states["numeric"][key]
    return states["colored"].get(key, states["numeric"][DEFAULT_PRESET])


def load_board_from_json(path: str | Path) -> Board:
    with open(path) as f:
        return json.load(f)
