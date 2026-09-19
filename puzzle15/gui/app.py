"""PuzzleApp: composition and wiring only.

No board math, no OpenCV, no algorithm dispatch lives here - those all
belong to solver/vision/integration. This class only builds the window,
owns AppState, and connects panel/dialog callbacks to the services.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from puzzle15.gui.dialogs.algorithm_settings_dialog import AlgorithmSettings, ask_algorithm_settings
from puzzle15.gui.dialogs.dev_console import DevConsole
from puzzle15.gui.dialogs.progress_dialog import ProgressDialog
from puzzle15.gui.dialogs.result_dialog import show_result
from puzzle15.gui.dialogs.scan_review_dialog import review_scan
from puzzle15.gui.logging_support import install_debug_log_handler
from puzzle15.gui.state import AppState
from puzzle15.gui.theme import COLORS, apply_style
from puzzle15.gui.widgets.buttons import make_button
from puzzle15.gui.widgets.panel_algorithms import AlgorithmsPanel
from puzzle15.gui.widgets.panel_goal import GoalStatePanel
from puzzle15.gui.widgets.panel_initial import InitialStatePanel
from puzzle15.integration.board_conversion import BoardValidationError, validate_board
from puzzle15.integration.scan_service import ScanService
from puzzle15.integration.solve_service import SolveService
from puzzle15.solver.board import Board
from puzzle15.solver.generator import generate_shuffled_board
from puzzle15.solver.goal_states import DEFAULT_PRESET, get_goal_state, load_board_from_json
from puzzle15.solver.registry import ALGORITHMS
from puzzle15.solver.result import SolveResult
from puzzle15.vision.result import ScanResult

WINDOW_SIZE = "1200x750"


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
        self.log_handler = install_debug_log_handler()
        self.dev_console: DevConsole | None = None

        wrapper = tk.Frame(root, bg=COLORS["bg"], padx=20, pady=20)
        wrapper.pack(fill=tk.BOTH, expand=True)

        top_bar = tk.Frame(wrapper, bg=COLORS["bg"])
        top_bar.pack(fill=tk.X, pady=(0, 10))
        make_button(top_bar, "Dev Console", self.handle_toggle_dev_console, COLORS["secondary"]).pack(side=tk.RIGHT)

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
        self.algorithms_panel = AlgorithmsPanel(main_container, on_select_algorithm=self.handle_select_algorithm)

        main_container.add(self.initial_panel, weight=1)
        main_container.add(self.goal_panel, weight=1)
        main_container.add(self.algorithms_panel, weight=1)

        self.goal_panel.update_board(self.state.goal_board)

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

    def handle_shuffle(self, difficulty: str) -> None:
        board = generate_shuffled_board(difficulty, self.state.goal_board)
        self.state.initial_board = board
        self.initial_panel.update_board(board)

    def handle_scan_photo(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png")])
        if not path:
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

    def _handle_scan_error(self, progress: ProgressDialog, exc: Exception) -> None:
        progress.close()
        messagebox.showerror("Scan failed", str(exc))

    # --- Goal state --------------------------------------------------------

    def handle_import_goal_json(self) -> None:
        board = self._import_board_from_json()
        if board is not None:
            self.state.goal_board = board
            self.goal_panel.update_board(board)

    def handle_select_preset(self, key: str) -> None:
        board = get_goal_state(key)
        self.state.goal_board = board
        self.goal_panel.update_board(board)

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

    # --- Solving -------------------------------------------------------------

    def handle_select_algorithm(self, algorithm_key: str) -> None:
        if self.state.initial_board is None:
            messagebox.showinfo("No initial state", "Set an initial state first (import, shuffle, or scan a photo).")
            return

        spec = ALGORITHMS[algorithm_key]
        settings = ask_algorithm_settings(self.root, spec)
        if settings is None:
            return

        progress = ProgressDialog(self.root, f"Running {spec.label}...")

        def on_done(result: SolveResult | None, error: Exception | None) -> None:
            self.root.after(0, lambda: self._handle_solve_done(progress, result, error))

        self.solve_service.run_async(
            algorithm_key,
            self.state.initial_board,
            self.state.goal_board,
            timeout=settings.timeout,
            max_depth=settings.max_depth,
            on_done=on_done,
        )

    def _handle_solve_done(self, progress: ProgressDialog, result: SolveResult | None, error: Exception | None) -> None:
        progress.close()
        if error is not None:
            messagebox.showerror("Solve failed", str(error))
            return
        show_result(self.root, result)


def run() -> None:
    root = tk.Tk()
    PuzzleApp(root)
    root.mainloop()


if __name__ == "__main__":
    run()
