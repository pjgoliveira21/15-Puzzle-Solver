# 15Puzzle: professional repo workflow, documentation, and Easy/Advanced mode UI

## Context

The 15Puzzle merge (search algorithms + photo recognition into one app) and a working PyInstaller exe build are already done and verified (52 tests passing, exe builds and runs correctly, confirmed interactively). This plan covers what comes next, in the order the user asked for:

1. **Turn this into a properly-run public repo.** No GitHub remote exists yet. The user wants branches + PRs + CI-gated merges, "professional... to be a reference public repo" — not just a pile of commits on `main`.
2. **Documentation and agent-context prep, before any new feature work.** An `AGENTS.md` (generic, not tool-specific) and an `ARCHITECTURE.md`, done as their own PR, so future sessions (human or AI) have real context to work from instead of re-deriving it.
3. **Then, the Easy/Advanced mode UI redesign** (v2): the user revealed a long-term goal of real-time webcam-based recognition and live solve guidance. For *this* pass they explicitly scoped it down to a mode split with no camera code yet — see the validated design below.

Each stage lands as its own branch + PR. Existing history (5 commits already on `main` from the merge) is **not** rewritten — the new workflow starts from the currently-uncommitted exe-build work forward.

## Stage 0 — GitHub repo + workflow scaffolding

**Branch:** `chore/repo-setup` (or similar) → PR → merge to `main`.

1. Create a new **public** GitHub repo named `15-Puzzle-Solver` (matches the naming pattern of the two source projects — `15-Puzzle-AI-Solver`, `15-Puzzle-Reader` — and the exe name already chosen). `gh` CLI is installed and authenticated (`poliveira-susplus`, `repo`+`workflow` scopes confirmed). Description: "A 15-puzzle solver with photo-based state recognition — search algorithms and OpenCV puzzle recognition merged into one desktop app."
2. Add it as `origin`, push existing `main` as the baseline (the 5 merge commits land as history, not retroactively split into PRs).
3. Commit the already-finished, already-tested PyInstaller packaging work (currently uncommitted: `puzzle15/paths.py` frozen-mode fix, `pyproject.toml` `build` extra, `puzzle15.spec`, `scripts/build_exe.py`, `.github/workflows/build-exe.yml`, `.gitignore` fix) on a feature branch, open a PR, merge it — this is the first real exercise of the new workflow.
4. Add `.github/PULL_REQUEST_TEMPLATE.md` (summary / test plan checklist, matching what this session's PR descriptions have actually looked like) and basic issue templates (`.github/ISSUE_TEMPLATE/bug_report.md`, `feature_request.md`).
5. Add a `LICENSE` — recommend **MIT** as a sensible default for a public reference/portfolio repo (README currently says "TBD"); flag this as a suggestion, easy to swap if the user wants something else.
6. Set up basic branch protection on `main`: require the `build-exe.yml` CI check to pass before merging, require PRs (no direct pushes). Not requiring approving reviews (solo maintainer) — just "CI must be green."
7. Branch naming convention to adopt going forward: `feat/*`, `fix/*`, `docs/*`, `chore/*`. Commit message style stays as-is (plain descriptive titles, already consistent across the 5 existing commits, with the `Co-Authored-By` trailer already in use).

## Stage 1 — Documentation & agent-context pass

**Branch:** `docs/architecture-and-agent-context` → PR → merge to `main`.

1. **`AGENTS.md`** (repo root, generic — not Claude-specific): project purpose, directory layout summary, key conventions and constraints an agent must respect (language-neutral algorithm keys in `solver/registry.py`; no business logic in `gui/` widgets — they only take callbacks; the `-1`/`None` boundary lives only in `integration/board_conversion.py`; GUI text is English; how to run tests (`pytest`) and build the exe (`python scripts/build_exe.py`); the branch/PR workflow from Stage 0). Points to `README.md` and `ARCHITECTURE.md` rather than duplicating their content.
2. **`ARCHITECTURE.md`**: the layered design (`solver` / `vision` / `integration` / `gui`) and *why* each boundary exists — the `-1`/`None` decision, the `AlgorithmSpec` registry pattern replacing the old string dispatch, the threaded-service pattern (`SolveService`/`ScanService`, background thread + callback), why dialogs don't reach back into the app instance, how `paths.py` resolves assets in both dev and frozen (PyInstaller) modes. Written so a new contributor (or agent) can navigate the codebase without re-reading every file.

## Stage 2 — Easy / Advanced mode UI (validated design, implement after Stage 1)

**Branch:** `feat/easy-advanced-mode` → PR → merge to `main`.

### What's changing and why
- Current top bar (just a "Dev Console" button) creates awkward dead space — user feedback. Replaced with a **native Tk menu bar**.
- User's real long-term goal: live webcam recognition + real-time solve guidance (explicitly **not** built this pass — see Roadmap below). This pass: mode split only, structured so a camera capture step can be swapped in later without a rewrite.
- **Easy mode**: "streamlined but still configurable, good defaults, almost just to know what's going on." The existing `InitialStatePanel`/`GoalStatePanel` already satisfy this (configurable, sensible preset default) — reused as-is. Only the third panel changes: instead of 5 algorithm-choice buttons, one **Solve** button (default algorithm A*, default timeout 30s, no settings dialog) that, once solved, shows **plain-language step-by-step move instructions** ("Move tile 12 up") with Prev/Next navigation — not the stats-heavy result dialog.
- **Advanced mode**: today's dashboard as-is, plus a **Compare Algorithms** action that runs all 5 algorithms against the current board and shows a results table (time/steps/explored/speed).
- Both modes share one `AppState` — switching mid-session doesn't lose the current board.

### File-by-file plan

**New:**

| File | Purpose |
|---|---|
| `puzzle15/solver/moves.py` | `MoveInstruction` dataclass (`tile`, `direction`, `from_pos`, `to_pos` — tile's own from/to, not the blank's) + `describe_moves(path: list[Board]) -> list[MoveInstruction]`. Derivation: for consecutive boards, `A = get_empty_position(prev)`, `B = get_empty_position(next)`; the moved tile is `next[A[0]][A[1]]`; it moved from `B` to `A`; direction from `(A[0]-B[0], A[1]-B[1])` mapped via the same `(-1,0)/(1,0)/(0,-1)/(0,1)` → up/down/left/right convention already used in `solver/board.py`'s `MOVES`. Add a defensive check that consecutive boards differ by exactly one adjacent swap. Pure, no GUI text (that's `panel_steps.py`'s job) — keeps `solver/` framework-agnostic per existing convention. |
| `puzzle15/integration/compare_service.py` | `CompareService.run_all_async(initial, goal, *, timeout, on_done: Callable[[dict[str, SolveResult]], None])` — thin `threading.Thread` wrapper (mirrors `SolveService`) around a new **synchronous, pure** `run_all_algorithms(initial, goal, *, timeout) -> dict[str, SolveResult]` in `solver/registry.py` (sequential loop over `ALGORITHMS` — sequential, not parallel, for predictable timing comparisons). Keeps real logic testable without threading, same pattern as `run_algorithm`. |
| `puzzle15/integration/capture.py` | `choose_photo_source(parent) -> Path \| None` — extracts the inline `filedialog.askopenfilename` currently in `app.py.handle_scan_photo` into its own function. This is the seam for a future webcam capture function with the same `Path \| None` contract; `ScanService`/`review_scan`/panels stay untouched when that's added later. |
| `puzzle15/gui/menu.py` | `build_menu_bar(root, *, mode_var: tk.StringVar, on_mode_change, on_toggle_dev_console) -> None`. **View** menu: Easy/Advanced radiobuttons. **Tools** menu: Dev Console. **Help** menu: About (simple messagebox). |
| `puzzle15/gui/widgets/panel_steps.py` | Easy mode's third panel. Three states: (a) no result yet → single "Solve" button; (b) solved → step navigator (reuses `BoardGrid`, showing `path[i]` + "Step i of N: Move tile X `<direction>`" + Prev/Next, using `BoardGrid.set_cell_highlight`) → failure message pointing to Advanced mode. |
| `puzzle15/gui/dialogs/compare_dialog.py` | `ask_comparison_timeout(parent) -> float \| None`; `show_comparison_results(parent, results: dict[str, SolveResult]) -> None` using a `ttk.Treeview` table (algorithm, success, time, steps, explored, speed). |

**Modified:**

| File | Change |
|---|---|
| `puzzle15/gui/app.py` | Drop the top-bar/Dev-Console-button; call `build_menu_bar`. Add `self.mode = tk.StringVar(value="easy")`. Third pane of the `PanedWindow` becomes one permanent `tk.Frame` holding both `AlgorithmsPanel` and the new `StepsPanel` stacked via `.grid(row=0, column=0, sticky="nsew")`, toggled with `.tkraise()` on mode change (**not** repeated `PanedWindow.forget()`/`.add()` — that can visibly shift sash proportions each toggle; pre-building both and raising is the standard Tk "page switch" idiom and keeps `PanedWindow` geometry stable). Add `handle_easy_solve`, `handle_compare_algorithms`. Route `handle_scan_photo` through `capture.choose_photo_source`. **Every board-mutating handler** (`handle_import_initial_json`, `handle_shuffle`, `_handle_scan_done`, `handle_import_goal_json`, `handle_select_preset`) calls `steps_panel.reset_to_ready()` so a stale step sequence never survives a board change. |
| `puzzle15/gui/widgets/panel_algorithms.py` | Add a 6th "Compare All" button + `on_compare: Callable[[], None]` param. |
| `puzzle15/solver/registry.py` | Add `run_all_algorithms(...)` (see above). Move `DEFAULT_TIMEOUT`/`DEFAULT_MAX_DEPTH` here from `gui/dialogs/algorithm_settings_dialog.py` so Easy mode's auto-solve, the Compare dialog, and the settings dialog all share one source instead of the dialog module being imported for constants. |

### Decisions carried from design review (flagged, not re-litigated)
- Step *i* shows `path[i]` (current state) with "do this next"; `Next` advances to `path[i+1]`; forward-compatible with the eventual live-camera guide shape (show observed state + next instruction).
- Compare-all failure semantics: fail-fast (abort + error), consistent with `SolveService`'s existing pattern, not partial-results-on-error.
- Default startup mode: Easy (not persisted across restarts this pass).
- Known minor tension left as-is: `InitialStatePanel`/`GoalStatePanel` both still expose "Import JSON" even in Easy mode — a power-user affordance not fully "streamlined," but the user's own answer endorsed reusing these panels unchanged; noted as a possible future Easy-mode polish, not addressed now.

### Tests to add
- `tests/solver/test_moves.py`: empty path → `[]`; one horizontal move (worked example: blank at (3,2)→(3,3), tile 15 moves left — matches existing `ONE_MOVE_AWAY`/`GOAL` fixtures in `test_algorithms.py`); one vertical move; round-trip check (solve a board, `describe_moves` the result path, replay each instruction and confirm it reproduces the next board in `path`); non-adjacent boards raise `ValueError`.
- `tests/solver/test_registry.py` (new, or extend `test_algorithms.py`): `run_all_algorithms` returns all 5 keys; already-at-goal → all succeed with 0 steps; vanishing timeout → all report failure.
- `tests/integration/test_compare_service.py`: first test for the threaded-service pattern (none exist yet for `SolveService`/`ScanService` either) — `threading.Event` set inside `on_done`, `.wait()`, assert the captured dict. One happy-path test; real logic is already covered by the `run_all_algorithms` unit tests.
- No new GUI-widget tests (matches existing project convention — zero tests under any `gui/` path today); keep `panel_steps.py`/`menu.py`/`compare_dialog.py` thin wiring/formatting only.

## Roadmap (documented for context, explicitly NOT built in this pass)

The user's actual end goal, staged for future sessions:
- **Stage A** (this plan, Stage 2 above): mode split, step-by-step instructions, algorithm comparison — all on static/file-picker image input.
- **Stage B**: single-shot webcam capture — one photo via camera through the existing scan pipeline, using the `capture.py` seam.
- **Stage C**: live preview prototype — periodic re-scan of a webcam feed; likely needs real performance work (the current template-matching pipeline was never built for interactive frame rates).
- **Stage D**: real-time move tracking — diff successive scans to detect the user's physical moves, re-plan/re-guide accordingly; likely needs recognition more robust than template matching given the lighting/angle sensitivity already measured in `tests/vision/expected_grids.json`.
- **Stage E**: full AR-style live-guided solving.

## Verification

- **Stage 0**: `gh repo view` confirms the remote exists and is public; PR for the packaging work merges cleanly through `gh pr merge`; branch protection confirmed via `gh api repos/{owner}/15-Puzzle-Solver/branches/main/protection`.
- **Stage 1**: docs PR merges; `AGENTS.md`/`ARCHITECTURE.md` reviewed for accuracy against the actual code (not aspirational).
- **Stage 2**: `pytest` green including new `test_moves.py`/`test_registry.py`/`test_compare_service.py`; manual run of `python main.py` — toggle Easy/Advanced via the menu, solve in Easy mode and confirm step instructions match an independently-verified short solve, run Compare Algorithms in Advanced mode and confirm the table's numbers are sane (DFS explored count typically far higher than A*'s, etc.), confirm switching modes mid-session preserves the board and confirm changing the board after an Easy-mode solve resets the steps panel.

## Status

Stages 0, 1, and 2 are complete and merged (PRs #1-#4). Stage B onward (Roadmap) is future work, not yet started.
