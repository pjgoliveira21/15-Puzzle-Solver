# Architecture

This document explains how `puzzle15` is put together and *why* — the
boundaries between packages exist on purpose, not by accident. See
[README.md](README.md) for what the app does and how to run it; this is
about how it's built.

## Layering

```
puzzle15/
├── solver/        framework-agnostic search algorithms + board logic
├── vision/          framework-agnostic photo -> grid recognition
├── integration/    the seam between solver/vision and the GUI
└── gui/               Tkinter app: widgets, dialogs, composition
```

The dependency direction is one-way: `gui` depends on `integration`,
`integration` depends on `solver`/`vision`, and `solver`/`vision` depend on
nothing above them. Neither imports `tkinter` or knows a GUI exists at
all — `vision` uses `cv2`/`numpy` because that's its actual job, but
nothing in either package has English UI strings, Tk types, or callbacks
shaped for a UI event loop. This means both packages are independently
testable and reusable — the entire `tests/solver` and `tests/vision`
suites run with no Tkinter window ever created.

## Why the board has two "empty" representations

The solver represents a board as a 4x4 `list[list[int]]` with **`-1`** as
the blank tile (`puzzle15/solver/board.py`). The vision pipeline produces a
grid where an unmatched cell is **`None`** (`puzzle15/vision/digit_reader.py`).

These are deliberately *not* unified early. `-1` means "this is the
puzzle's blank tile" — a fact about the puzzle. `None` means "template
matching didn't confidently recognize a digit here" — a fact about the
recognition attempt, which could be the blank tile, or could be tile `7`
that got misread because of glare. Collapsing them at the vision boundary
would silently turn a misread into a blank tile.

The translation happens in exactly one place, and only when a human
confirms it: `puzzle15/integration/board_conversion.py`.

```python
def scan_grid_to_board(grid: list[list[int | None]]) -> Board:
    """None -> -1. Raises BoardValidationError if not exactly one None."""

def validate_board(board: Board) -> None:
    """4x4, exactly one -1, values 1-15 each exactly once."""
```

The GUI's scan review dialog (`gui/dialogs/scan_review_dialog.py`) shows
the raw vision grid — unmatched cells highlighted distinctly from
low-confidence-but-matched cells — and only calls `scan_grid_to_board`
once the user accepts it.

## The algorithm registry

`puzzle15/solver/registry.py` holds an `AlgorithmSpec` per algorithm
(`dfs`/`bfs`/`gbfs`/`astar`/`idastar`), keyed by a stable, language-neutral
string. The GUI never has an `if algo == "Depth-First Search"` chain — it
looks up a spec by key and calls `spec.solve(...)`. The **display label**
lives on the spec, not hardcoded in GUI widgets — if the label needs to
change or the app needs a second language, that's a one-line edit in the
registry, not a hunt through button-construction code.

```python
@dataclass(frozen=True)
class AlgorithmSpec:
    key: str            # "astar" - stable, never shown to a user
    label: str            # "A*" - the only place English wording lives
    solve: Callable[..., SolveResult]
    supports_max_depth: bool = False
```

## Threaded services: the pattern, and why it looks like this

A search can run for tens of seconds; a scan does a perspective warp plus
up to 15×16 template-match calls. Both would freeze the UI if run on
Tkinter's main thread. `puzzle15/integration/solve_service.py` and
`scan_service.py` share one shape:

```python
class SolveService:
    def run_async(self, algorithm_key, initial, goal, *, timeout, max_depth, on_done):
        def run():
            try:
                result = run_algorithm(...)
                on_done(result, None)
            except Exception as exc:
                on_done(None, exc)
        threading.Thread(target=run, daemon=True).start()
```

Callbacks fire **on the worker thread**, not the main thread — callers
in `gui/app.py` wrap them in `root.after(0, ...)` before touching any Tk
widget from inside `on_done`/`on_error`. The service itself has no Tkinter
knowledge; it's testable with a plain `threading.Event`.

This mirrors (and fixes) the original AI-Solver project's `bridge.py`,
which called its error callback *and then re-raised* inside the daemon
thread — the re-raise reached no handler and just dumped a traceback. The
services here call the callback exactly once and never re-raise.

## Why dialogs don't reach into the app instance

`gui/dialogs/result_dialog.py`'s `show_result()` builds its own
`BoardGrid` and owns its own step-playback loop (`popup.after(...)`)
instead of calling back into `PuzzleApp.render_matrix()`/`start_playback()`
methods. Every dialog function takes what it needs as parameters and
returns a plain value (or `None` on cancel) — no dialog holds a reference
to `PuzzleApp`. This is what makes `gui/dialogs/` independently readable:
opening any one file tells you everything it depends on.

`gui/app.py` is the only file that wires panels, dialogs, and services
together. It contains no board math, no OpenCV, and no algorithm dispatch
of its own — if you're looking for *business logic* and you're reading
`app.py`, you're in the wrong file.

## Asset resolution: dev vs. frozen

`puzzle15/paths.py` resolves `assets/` two different ways depending on
whether the app is running from source or from a PyInstaller-frozen
build:

```python
if getattr(sys, "frozen", False):
    PROJECT_ROOT = Path(sys._MEIPASS)   # PyInstaller's extraction dir
else:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
```

`puzzle15.spec` bundles `assets/` into the executable under the same
relative path, so every other module that imports from `paths.py` (goal
states, digit masks, sample photos) needs no knowledge of which mode it's
running in.

## Testing philosophy

- `solver/` and `vision/` are pure enough to unit test without any I/O
  beyond reading bundled JSON/images — see `tests/solver/`, `tests/vision/`.
- `vision.scanner` end-to-end tests run against the 6 bundled real sample
  photos, asserting a **minimum match rate** per photo (not exact
  equality) — see `tests/vision/test_scanner_samples.py` and
  `tests/vision/expected_grids.json`. Template matching is genuinely
  sensitive to lighting/angle; an exact-match assertion would be flaky by
  design, so each photo's threshold reflects its measured, real difficulty.
- `integration/` has one test file today (`test_board_conversion.py`) —
  the threaded services (`SolveService`/`ScanService`) don't have
  dedicated tests yet; they're currently verified by the pure functions
  they wrap (`run_algorithm`, `PuzzleScanner.scan_file`) plus manual runs.
- `gui/` has zero automated tests. Tkinter widget trees aren't practically
  unit-testable here — GUI changes are verified by running `python main.py`
  and exercising the change manually. This is a known, accepted gap, not
  an oversight.

## Extension points

- **A different image source for "Scan Photo"** (e.g. a webcam capture):
  the seam is wherever the GUI currently picks a file path and hands it to
  `ScanService.scan_file_async`. `PuzzleScanner`/`ScanService` don't care
  where the path came from.
- **A new search algorithm**: implement `solve_x(initial, goal, timeout) ->
  SolveResult` in `solver/algorithms/`, register it in
  `solver/registry.py`. Nothing in `gui/` or `integration/` needs to change.
- **A different recognition approach**: `vision/digit_reader.py`'s
  `read_numbers()` is the only place that knows template matching is the
  technique in use; it returns the same `(grid, scores, cells_processed)`
  shape regardless of how it got there.
