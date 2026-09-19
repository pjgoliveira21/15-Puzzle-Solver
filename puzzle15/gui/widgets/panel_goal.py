import tkinter as tk
from typing import Callable

from puzzle15.gui.theme import COLORS
from puzzle15.gui.widgets.board_grid import BoardGrid
from puzzle15.gui.widgets.buttons import make_button
from puzzle15.solver.board import Board
from puzzle15.solver.goal_states import PRESET_KEYS

PRESET_LABELS = {
    "row_asc": "Rows Ascending",
    "row_desc": "Rows Descending",
    "col_asc": "Columns Ascending",
    "col_desc": "Columns Descending",
}


class GoalStatePanel(tk.Frame):
    def __init__(self, parent, *, on_import_json: Callable[[], None], on_select_preset: Callable[[str], None], **kwargs):
        super().__init__(parent, bg=COLORS["card"], padx=15, pady=15, highlightbackground="#dcdde1", highlightthickness=1, **kwargs)

        tk.Label(self, text="GOAL STATE", font=("Segoe UI", 11, "bold"), bg=COLORS["card"], fg=COLORS["secondary"]).pack(pady=(0, 15))
        make_button(self, "Import JSON", on_import_json, COLORS["primary"]).pack(fill=tk.X, pady=5)

        presets_frame = tk.Frame(self, bg=COLORS["card"])
        presets_frame.pack(fill=tk.X, pady=5)
        for key in PRESET_KEYS:
            tk.Button(
                presets_frame,
                text=PRESET_LABELS[key],
                font=("Segoe UI", 9),
                bg="#f8f9fa",
                fg=COLORS["text"],
                relief="flat",
                command=lambda k=key: on_select_preset(k),
            ).pack(fill=tk.X, pady=2)

        tk.Frame(self, height=2, bg="#f5f6fa").pack(fill=tk.X, pady=20)
        self.board_widget = BoardGrid(self)
        self.board_widget.pack(expand=True)

    def update_board(self, board: Board) -> None:
        self.board_widget.set_board(board)
