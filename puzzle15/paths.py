"""Centralized, CWD-independent paths to bundled assets."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
GOAL_STATES_PATH = ASSETS_DIR / "goal_states.json"
MASKS_DIR = ASSETS_DIR / "masks"
SAMPLE_PUZZLES_DIR = ASSETS_DIR / "sample_puzzles"
