"""PuzzleApp: composition and wiring only.

No board math, no OpenCV, no algorithm dispatch lives here - those all
belong to solver/vision/integration. This class only builds the window,
owns AppState, and connects panel/dialog callbacks to the services.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from puzzle15.gui.dialogs.algorithm_settings_dialog import AlgorithmSettings, ask_algorithm_settings
from puzzle15.gui.dialogs.compare_dialog import ask_comparison_timeout, show_comparison_results
from puzzle15.gui.dialogs.dev_console import DevConsole
from puzzle15.gui.dialogs.progress_dialog import ProgressDialog
from puzzle15.gui.dialogs.result_dialog import show_result
from puzzle15.gui.dialogs.scan_review_dialog import review_scan
from puzzle15.gui.logging_support import install_debug_log_handler
from puzzle15.gui.menu import build_menu_bar
from puzzle15.gui.state import AppState
from puzzle15.gui.theme import COLORS, apply_style
from puzzle15.gui.widgets.panel_algorithms import AlgorithmsPanel
from puzzle15.gui.widgets.panel_goal import GoalStatePanel
from puzzle15.gui.widgets.panel_initial import InitialStatePanel
from puzzle15.gui.widgets.panel_steps import StepsPanel
from puzzle15.integration.board_conversion import BoardValidationError, validate_board
from puzzle15.integration.capture import choose_photo_source
from puzzle15.integration.compare_service import CompareService
from puzzle15.integration.scan_service import ScanService
from puzzle15.integration.solve_service import SolveService
from puzzle15.solver.board import Board
from puzzle15.solver.generator import generate_shuffled_board
from puzzle15.solver.goal_states import DEFAULT_PRESET, get_goal_state, load_board_from_json
from puzzle15.solver.registry import ALGORITHMS, DEFAULT_TIMEOUT
from puzzle15.solver.result import SolveResult
from puzzle15.vision.result import ScanResult

WINDOW_SIZE = "1200x750"
EASY_MODE_ALGORITHM = "astar"


class PuzzleApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("15-Puzzle Solver")
        self.root.geometry(WINDOW_SIZE)
        self.root.configure(bg=COLORS["bg"])

        apply_style(ttk.Style())

        self.state = AppState(goal_board=get_goal_state(DEFAULT_PRESET))
        self.solve_service = SolveService()
        self.scan_service = ScanService()
        self.compare_service = CompareService()
        self.log_handler = install_debug_log_handler()
        self.dev_console: DevConsole | None = None
        self.mode = tk.StringVar(value="easy")
        # Bumped on every board-mutating handler; async solve/compare
        # callbacks capture this at request time and ignore their own
        # result if it no longer matches, so a board change mid-search
        # can't display a result for a board that's no longer on screen.
        self._board_version = 0

        build_menu_bar(
            self.root,
            mode_var=self.mode,
            on_mode_change=self.handle_mode_change,
            on_toggle_dev_console=self.handle_toggle_dev_console,
        )

        wrapper = tk.Frame(root, bg=COLORS["bg"], padx=20, pady=20)
        wrapper.pack(fill=tk.BOTH, expand=True)

        main_container = ttk.PanedWindow(wrapper, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True)

        self.initial_panel = InitialStatePanel(
            main_container,
            on_import_json=self.handle_import_initial_json,
            on_shuffle=self.handle_shuffle,
            on_scan_photo=self.handle_scan_photo,
        )
        self.goal_panel = GoalStatePanel(
            main_container,
            on_import_json=self.handle_import_goal_json,
            on_select_preset=self.handle_select_preset,
        )

        # Easy mode's StepsPanel and Advanced mode's AlgorithmsPanel are
        # both built once as permanent siblings in the same cell and
        # switched with .tkraise() on mode change, rather than being
        # forgotten/re-added to the PanedWindow - that would shift the
        # sash proportions on every toggle.
        third_pane = tk.Frame(main_container, bg=COLORS["card"])
        third_pane.grid_rowconfigure(0, weight=1)
        third_pane.grid_columnconfigure(0, weight=1)

        self.algorithms_panel = AlgorithmsPanel(
            third_pane,
            on_select_algorithm=self.handle_select_algorithm,
            on_compare=self.handle_compare_algorithms,
        )
        self.steps_panel = StepsPanel(third_pane, on_solve=self.handle_easy_solve)
        self.algorithms_panel.grid(row=0, column=0, sticky="nsew")
        self.steps_panel.grid(row=0, column=0, sticky="nsew")

        main_container.add(self.initial_panel, weight=1)
        main_container.add(self.goal_panel, weight=1)
        main_container.add(third_pane, weight=1)

        self.goal_panel.update_board(self.state.goal_board)
        self.handle_mode_change()

    # --- Mode switch -------------------------------------------------------

    def handle_mode_change(self) -> None:
        if self.mode.get() == "easy":
            self.steps_panel.tkraise()
        else:
            self.algorithms_panel.tkraise()

    # --- Dev console -----------------------------------------------------

    def handle_toggle_dev_console(self) -> None:
        if self.dev_console is not None and self.dev_console.window.winfo_exists():
            self.dev_console.focus()
            return
        self.dev_console = DevConsole(self.root, self.log_handler)

    # --- Initial state ---------------------------------------------------

    def handle_import_initial_json(self) -> None:
        board = self._import_board_from_json()
        if board is not None:
            self.state.initial_board = board
            self.initial_panel.update_board(board)
            self._on_board_changed()

    def handle_shuffle(self, difficulty: str) -> None:
        board = generate_shuffled_board(difficulty, self.state.goal_board)
        self.state.initial_board = board
        self.initial_panel.update_board(board)
        self._on_board_changed()

    def handle_scan_photo(self) -> None:
        path = choose_photo_source(self.root)
        if path is None:
            return

        progress = ProgressDialog(self.root, "Scanning photo...")

        def on_done(scan_result: ScanResult) -> None:
            self.root.after(0, lambda: self._handle_scan_done(progress, scan_result))

        def on_error(exc: Exception) -> None:
            self.root.after(0, lambda: self._handle_scan_error(progress, exc))

        self.scan_service.scan_file_async(path, on_done=on_done, on_error=on_error)

    def _handle_scan_done(self, progress: ProgressDialog, scan_result: ScanResult) -> None:
        progress.close()
        board = review_scan(self.root, scan_result)
        if board is not None:
            self.state.initial_board = board
            self.initial_panel.update_board(board)
            self._on_board_changed()

    def _handle_scan_error(self, progress: ProgressDialog, exc: Exception) -> None:
        progress.close()
        messagebox.showerror("Scan failed", str(exc))

    # --- Goal state --------------------------------------------------------

    def handle_import_goal_json(self) -> None:
        board = self._import_board_from_json()
        if board is not None:
            self.state.goal_board = board
            self.goal_panel.update_board(board)
            self._on_board_changed()

    def handle_select_preset(self, key: str) -> None:
        board = get_goal_state(key)
        self.state.goal_board = board
        self.goal_panel.update_board(board)
        self._on_board_changed()

    def _on_board_changed(self) -> None:
        self._board_version += 1
        self.steps_panel.reset_to_ready()

    def _import_board_from_json(self) -> Board | None:
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not path:
            return None
        try:
            board = load_board_from_json(path)
            validate_board(board)
        except (OSError, ValueError, BoardValidationError) as exc:
            messagebox.showerror("Invalid board", str(exc))
            return None
        return board

    # --- Solving (Advanced mode) --------------------------------------------

    def handle_select_algorithm(self, algorithm_key: str) -> None:
        if self.state.initial_board is None:
            messagebox.showinfo("No initial state", "Set an initial state first (import, shuffle, or scan a photo).")
            return

        spec = ALGORITHMS[algorithm_key]
        settings = ask_algorithm_settings(self.root, spec)
        if settings is None:
            return

        progress = ProgressDialog(self.root, f"Running {spec.label}...")
        request_version = self._board_version

        def on_done(result: SolveResult | None, error: Exception | None) -> None:
            self.root.after(0, lambda: self._handle_solve_done(progress, result, error, request_version))

        self.solve_service.run_async(
            algorithm_key,
            self.state.initial_board,
            self.state.goal_board,
            timeout=settings.timeout,
            max_depth=settings.max_depth,
            on_done=on_done,
        )

    def _handle_solve_done(
        self,
        progress: ProgressDialog,
        result: SolveResult | None,
        error: Exception | None,
        request_version: int,
    ) -> None:
        progress.close()
        if request_version != self._board_version:
            return
        if error is not None:
            messagebox.showerror("Solve failed", str(error))
            return
        show_result(self.root, result)

    def handle_compare_algorithms(self) -> None:
        if self.state.initial_board is None:
            messagebox.showinfo("No initial state", "Set an initial state first (import, shuffle, or scan a photo).")
            return

        timeout = ask_comparison_timeout(self.root)
        if timeout is None:
            return

        progress = ProgressDialog(self.root, "Comparing algorithms...")
        request_version = self._board_version

        def on_done(results: dict[str, SolveResult] | None, error: Exception | None) -> None:
            self.root.after(0, lambda: self._handle_compare_done(progress, results, error, request_version))

        self.compare_service.run_all_async(
            self.state.initial_board,
            self.state.goal_board,
            timeout=timeout,
            on_done=on_done,
        )

    def _handle_compare_done(
        self,
        progress: ProgressDialog,
        results: dict[str, SolveResult] | None,
        error: Exception | None,
        request_version: int,
    ) -> None:
        progress.close()
        if request_version != self._board_version:
            return
        if error is not None:
            messagebox.showerror("Comparison failed", str(error))
            return
        show_comparison_results(self.root, results)

    # --- Solving (Easy mode) -------------------------------------------------

    def handle_easy_solve(self) -> None:
        if self.state.initial_board is None:
            messagebox.showinfo("No initial state", "Set an initial state first (import, shuffle, or scan a photo).")
            return

        progress = ProgressDialog(self.root, "Solving...")
        request_version = self._board_version

        def on_done(result: SolveResult | None, error: Exception | None) -> None:
            self.root.after(0, lambda: self._handle_easy_solve_done(progress, result, error, request_version))

        self.solve_service.run_async(
            EASY_MODE_ALGORITHM,
            self.state.initial_board,
            self.state.goal_board,
            timeout=DEFAULT_TIMEOUT,
            on_done=on_done,
        )

    def _handle_easy_solve_done(
        self,
        progress: ProgressDialog,
        result: SolveResult | None,
        error: Exception | None,
        request_version: int,
    ) -> None:
        progress.close()
        if request_version != self._board_version:
            return
        if error is not None:
            messagebox.showerror("Solve failed", str(error))
            return
        self.steps_panel.show_result(result)


def run() -> None:
    root = tk.Tk()
    PuzzleApp(root)
    root.mainloop()


if __name__ == "__main__":
    run()
