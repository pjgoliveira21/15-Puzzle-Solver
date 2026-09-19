# 15-Puzzle Solver

A desktop app that solves the [15-puzzle](https://en.wikipedia.org/wiki/15_puzzle) sliding-tile game — either from a manually entered/generated board, or from a photo of a physical puzzle.

## Features

- Five search algorithms: Depth-First Search, Breadth-First Search, Greedy Best-First Search, A*, and Iterative Deepening A*, each with configurable timeout (and max depth, for DFS).
- Goal-state presets (rows/columns ascending/descending) or import your own from JSON.
- Shuffle generator (easy/normal/hard) for a random solvable initial state.
- **Scan Photo**: point it at a photo of a physical 15-puzzle and it recognizes the board via computer vision, with a review step to fix any misread tile before solving.
- Step-by-step playback of the found solution.
- A Dev Console toggle to watch live debug logs from the solver and vision pipeline while the app runs.

## Requirements

- Python 3.10+
- Tkinter (bundled with most Python installs; on Linux you may need `python3-tk` from your package manager)
- OpenCV and NumPy (installed automatically, see below)

## Installation

```bash
pip install -e ".[dev]"
```

The `dev` extra pulls in `pytest` and `matplotlib` (used only by the optional vision debug CLI). For a minimal install without dev/debug tooling, use `pip install -e .` instead.

## Usage

Run the app:

```bash
python main.py
```

Or, after installing:

```bash
puzzle15
```

### Vision debug CLI

To inspect the scan pipeline's intermediate steps (perspective warp, segmentation, per-cell recognition) against one of the bundled sample photos:

```bash
python -m puzzle15.vision.debug_cli puzzle1
```

## Project structure

```
puzzle15/
├── solver/        # search algorithms, board/state logic, goal-state presets, shuffle generator
├── vision/         # photo -> grid: perspective correction, segmentation, template-matching digit recognition
├── integration/     # the -1/None boundary between vision and solver, threaded services for the GUI
└── gui/             # Tkinter app - panels, dialogs, and app.py (composition/wiring only)
assets/               # digit masks, sample puzzle photos, goal-state presets
tests/                # solver/vision/integration test suites
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for why the package boundaries are drawn where they are. Contributing (including AI agents) should also read [AGENTS.md](AGENTS.md).

## How "Scan Photo" works

1. `vision.perspective` locates the puzzle's red/white frame in the photo and warps it to a top-down view.
2. `vision.segmentation` isolates the digit-bearing region.
3. `vision.digit_reader` recognizes each cell's digit via template matching against 15 pre-made masks (largest digit first, global best-match assignment).
4. The recognized grid is shown in a review dialog — cells with no confident match are marked red, low-confidence matches are marked amber — where you can correct any cell before accepting it as the puzzle's initial state.

This review step exists because template matching isn't perfect: lighting, angle, and occlusion in a real photo can cause misreads (see Known limitations below), and the two source projects this app was merged from were never actually connected with any validation between them.

## Architecture notes

The solver represents the blank tile as `-1`; the vision pipeline represents "no digit matched confidently" as `None`. These are kept as distinct concepts until the user explicitly accepts a scan (`puzzle15.integration.board_conversion`) — an unmatched cell is never silently treated as the puzzle's blank tile. See [ARCHITECTURE.md](ARCHITECTURE.md) for the full picture (package layering, the threaded-service pattern, testing philosophy, extension points).

## Testing

```bash
pytest                   # everything (all suites run in well under a second)
pytest -m "not slow"      # skip the end-to-end scans against real sample photos
```

Tests marked `slow` aren't slow in wall-clock terms here — the marker exists to separate deterministic unit tests from end-to-end tests against real photos, whose exact recognition output can be more sensitive to the OpenCV/NumPy version in use.

The GUI itself isn't covered by automated tests (Tkinter widget trees aren't practically unit-testable here) — verify GUI changes with a manual run of `python main.py`.

## Known limitations

Template-matching digit recognition is sensitive to lighting, camera angle, and occlusion in the source photo — some of the bundled sample photos recognize perfectly, others only partially (see `tests/vision/test_scanner_samples.py` and `tests/vision/expected_grids.json` for the measured accuracy per sample). The review dialog exists specifically to catch and correct these misreads before solving.

## Credits

Merged from two earlier projects: **15-Puzzle-AI-Solver** (search algorithms and desktop UI) and **15-Puzzle-Reader** (OpenCV-based puzzle recognition), rebuilt into one architecture with the solver, vision, and GUI code cleanly separated.

## License

[MIT](LICENSE)
