"""Centralized, CWD-independent paths to bundled assets.

Works both from source and from a PyInstaller-frozen build: PyInstaller
extracts bundled data files under sys._MEIPASS (onefile) or next to the
executable (onedir) at runtime, rather than leaving them next to this
source file - see puzzle15.spec's `datas` for what gets bundled there.
"""

import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    PROJECT_ROOT = Path(sys._MEIPASS)  # type: ignore[attr-defined]
else:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent

ASSETS_DIR = PROJECT_ROOT / "assets"
GOAL_STATES_PATH = ASSETS_DIR / "goal_states.json"
MASKS_DIR = ASSETS_DIR / "masks"
SAMPLE_PUZZLES_DIR = ASSETS_DIR / "sample_puzzles"
