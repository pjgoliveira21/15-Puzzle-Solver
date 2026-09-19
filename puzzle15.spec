# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for the 15-Puzzle Solver desktop app.

Build locally with:
    pyinstaller puzzle15.spec
or the convenience wrapper:
    python scripts/build_exe.py

Produces a single-file Windows executable at dist/15-Puzzle-Solver.exe.
Bundled data files (digit masks, sample puzzle photos, goal-state presets)
are extracted to sys._MEIPASS at runtime - see puzzle15/paths.py.
"""

block_cipher = None

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("assets", "assets"),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # matplotlib is only used by the optional vision debug CLI, never imported
    # by the GUI app itself - excluded to keep the build smaller.
    excludes=["matplotlib", "pytest", "IPython"],
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="15-Puzzle-Solver",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
