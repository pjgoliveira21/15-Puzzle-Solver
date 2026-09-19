import tkinter as tk
from typing import Callable

from puzzle15.gui.dialogs.shuffle_dialog import ask_difficulty
from puzzle15.gui.theme import COLORS
from puzzle15.gui.widgets.board_grid import BoardGrid
from puzzle15.gui.widgets.buttons import make_button
from puzzle15.solver.board import Board


class InitialStatePanel(tk.Frame):
    def __init__(
        self,
        parent,
        *,
        on_import_json: Callable[[], None],
        on_shuffle: Callable[[str], None],
        on_scan_photo: Callable[[], None],
        **kwargs,
    ):
        super().__init__(parent, bg=COLORS["card"], padx=15, pady=15, highlightbackground="#dcdde1", highlightthickness=1, **kwargs)

        tk.Label(self, text="INITIAL STATE", font=("Segoe UI", 11, "bold"), bg=COLORS["card"], fg=COLORS["secondary"]).pack(pady=(0, 15))
        make_button(self, "Import JSON", on_import_json, COLORS["primary"]).pack(fill=tk.X, pady=5)
        make_button(self, "Scan Photo", on_scan_photo, COLORS["accent"]).pack(fill=tk.X, pady=5)
        make_button(self, "Shuffle Puzzle", lambda: self._handle_shuffle(on_shuffle), COLORS["secondary"]).pack(fill=tk.X, pady=5)

        tk.Frame(self, height=2, bg="#f5f6fa").pack(fill=tk.X, pady=20)
        self.board_widget = BoardGrid(self)
        self.board_widget.pack(expand=True)

    def _handle_shuffle(self, on_shuffle: Callable[[str], None]) -> None:
        difficulty = ask_difficulty(self)
        if difficulty is not None:
            on_shuffle(difficulty)

    def update_board(self, board: Board) -> None:
        self.board_widget.set_board(board)
