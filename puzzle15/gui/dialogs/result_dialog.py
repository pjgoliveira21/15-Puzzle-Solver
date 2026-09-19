"""Solve result popup with step-playback.

Unlike the original ui/popups.py's show_result_window, this owns its own
BoardGrid and playback loop instead of reaching back into the PuzzleApp
instance's render_matrix/start_popup_playback/_play_popup_step methods.
"""

import tkinter as tk
from tkinter import ttk

from puzzle15.gui.dialogs._common import make_popup_header
from puzzle15.gui.theme import COLORS
from puzzle15.gui.widgets.board_grid import BoardGrid
from puzzle15.gui.widgets.buttons import make_button
from puzzle15.solver.result import SolveResult

PLAYBACK_STEP_MS = 400


def show_result(parent, result: SolveResult) -> None:
    popup = tk.Toplevel(parent)
    popup.title("Search Results")
    popup.geometry("450x700")
    popup.resizable(False, False)
    popup.grab_set()

    header_color = COLORS["success"] if result.success else COLORS["danger"]
    status_text = "SOLUTION FOUND" if result.success else "SEARCH INTERRUPTED"
    make_popup_header(popup, status_text, header_color)

    metrics_frame = tk.Frame(popup, padx=40, pady=20)
    metrics_frame.pack(fill=tk.X)

    def add_metric(row: int, label: str, value: str) -> None:
        tk.Label(metrics_frame, text=label, font=("Segoe UI", 10), fg="#7f8c8d").grid(row=row, column=0, sticky="w", pady=5)
        tk.Label(metrics_frame, text=value, font=("Segoe UI", 10, "bold")).grid(row=row, column=1, sticky="e", pady=5)
        metrics_frame.grid_columnconfigure(1, weight=1)

    nps = result.explored / result.time_seconds if result.time_seconds > 0 else 0
    add_metric(0, "Elapsed time:", f"{result.time_seconds}s")
    add_metric(1, "Nodes explored:", f"{result.explored:,}")
    add_metric(2, "Average speed:", f"{nps:.0f} NPS")
    if result.success:
        add_metric(3, "Total steps:", f"{result.steps} moves")

    ttk.Separator(popup, orient="horizontal").pack(fill=tk.X, padx=30, pady=10)

    board_container = tk.Frame(popup, pady=10)
    board_container.pack()

    if result.success and result.path:
        board_widget = BoardGrid(board_container)
        board_widget.pack()
        board_widget.set_board(result.path[0])

        def play_step(index: int) -> None:
            if not popup.winfo_exists():
                return
            if index < len(result.path):
                board_widget.set_board(result.path[index])
                popup.after(PLAYBACK_STEP_MS, lambda: play_step(index + 1))

        footer = tk.Frame(popup, pady=20)
        footer.pack()
        make_button(footer, "▶ PLAY STEPS", lambda: play_step(0), COLORS["primary"]).pack(pady=5)

    make_button(popup, "CLOSE", popup.destroy, COLORS["secondary"]).pack(side=tk.BOTTOM, pady=20, padx=20, fill=tk.X)
