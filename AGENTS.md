# AGENTS.md

Context for AI coding agents working in this repo. Generic on purpose —
not tied to any one tool. If you're a human, [README.md](README.md) and
[ARCHITECTURE.md](ARCHITECTURE.md) are probably what you want instead.

## What this is

A 15-puzzle solver desktop app (Python/Tkinter): five search algorithms
(DFS/BFS/GBFS/A*/IDA*) plus OpenCV-based recognition of a physical
puzzle's state from a photo. Originally two separate school projects,
merged into one architecture. See [README.md](README.md) for features and
[ARCHITECTURE.md](ARCHITECTURE.md) for the package layering and the
reasoning behind its boundaries — read that before making structural
changes, not just this file.

## Layout at a glance

```
puzzle15/solver/        search algorithms, board/state logic - no GUI, no vision
puzzle15/vision/          photo -> grid recognition (OpenCV) - no GUI, no solver
puzzle15/integration/    the -1/None boundary, threaded services for the GUI
puzzle15/gui/               Tkinter app - widgets/dialogs/panels + app.py wiring
assets/                        digit masks, sample puzzle photos, goal-state presets
tests/                          mirrors the solver/vision/integration structure
```

## Conventions to respect

- **Algorithm keys are language-neutral, labels aren't.** `solver/registry.py`'s
  `AlgorithmSpec.key` (`"astar"`, `"dfs"`, ...) is used for dispatch and must
  never change casually. `AlgorithmSpec.label` is the only place
  display text lives — don't hardcode algorithm names in `gui/` widgets.
- **`gui/` widgets take callbacks, not logic.** Panels and dialogs receive
  callables from `gui/app.py` and call them on user action; they don't
  import `solver`/`vision`/`integration` to do work themselves (a couple
  of read-only exceptions exist, e.g. a panel reading `ALGORITHMS` to
  build button labels — that's fine; running a solve or a scan is not).
  If you're about to write board math or an OpenCV call inside a
  `gui/widgets/*.py` or `gui/dialogs/*.py` file, it belongs in
  `solver/`, `vision/`, or `integration/` instead.
- **The `-1`/`None` boundary is intentional, not a bug.** Don't "simplify"
  by converting vision's `None` to `-1` earlier than
  `integration/board_conversion.py`. See ARCHITECTURE.md for why.
- **GUI text is English.** (The two source projects it was merged from
  were Portuguese; this was an explicit decision when merging, not an
  oversight.)
- **Services fire callbacks on a worker thread.** `SolveService`/`ScanService`
  run in a background `threading.Thread` and call `on_done`/`on_error`
  from that thread. Any Tkinter widget touch inside those callbacks must
  be wrapped in `root.after(0, ...)` by the caller — the services
  themselves have no Tkinter knowledge and shouldn't gain any.
- **Same technique, ported deliberately.** The search algorithms and the
  OpenCV recognition approach (perspective warp + HSV segmentation +
  template matching) were carried over from the two source projects
  on purpose — this is an architecture rewrite, not an algorithm
  rewrite. Don't swap in a different CV/ML approach or a different
  search technique without it being an explicit, separate decision.

## Running things

```bash
pip install -e ".[dev]"     # or ".[dev,build]" to also get PyInstaller
pytest                       # full suite, well under a second
pytest -m "not slow"          # skip the real-photo end-to-end scans
python main.py                 # run the app
python -m puzzle15.vision.debug_cli puzzle1   # vision pipeline debug CLI
python scripts/build_exe.py     # build a standalone Windows exe (PyInstaller)
```

## Before proposing a change

- If it touches `solver/` or `vision/`, there's almost certainly a test
  file to extend (`tests/solver/`, `tests/vision/`) — this repo has real
  test coverage for the non-GUI layers, use it.
- If it touches `gui/`, there are no automated tests to lean on
  (documented, accepted gap — see ARCHITECTURE.md's Testing section).
  Verify by actually running `python main.py`, not just by reading the
  diff.
- Run `pytest` before considering any change done.

## Git workflow

- Branches: `feat/*`, `fix/*`, `docs/*`, `chore/*`.
- `main` is protected: changes land via PR, and the `build` CI check
  (`.github/workflows/build-exe.yml` — runs the test suite, then builds
  the exe) must pass before merging.
- Commit messages: plain descriptive titles (not Conventional Commits
  prefixes) with a body explaining *why* when it's not obvious from the
  diff. Existing commit history is the style guide.
