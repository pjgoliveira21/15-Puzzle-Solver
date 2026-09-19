#!/usr/bin/env python
"""Build a standalone Windows executable via PyInstaller.

Usage:
    pip install -e ".[build]"
    python scripts/build_exe.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SPEC_FILE = PROJECT_ROOT / "puzzle15.spec"
EXPECTED_EXE = PROJECT_ROOT / "dist" / "15-Puzzle-Solver.exe"


def main() -> None:
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print('PyInstaller is not installed. Run: pip install -e ".[build]"', file=sys.stderr)
        raise SystemExit(1)

    for stale_dir in ("build", "dist"):
        shutil.rmtree(PROJECT_ROOT / stale_dir, ignore_errors=True)

    subprocess.run(
        [sys.executable, "-m", "PyInstaller", str(SPEC_FILE), "--noconfirm"],
        cwd=PROJECT_ROOT,
        check=True,
    )

    if not EXPECTED_EXE.exists():
        print(f"\nBuild finished but {EXPECTED_EXE} wasn't found.", file=sys.stderr)
        raise SystemExit(1)

    print(f"\nBuilt: {EXPECTED_EXE}")


if __name__ == "__main__":
    main()
