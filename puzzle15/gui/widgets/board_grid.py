"""BoardGrid: the single reusable 4x4 tile widget.

Used by every panel and dialog that displays a board (initial/goal panels,
the result playback dialog, the scan review dialog) instead of each of them
rebuilding its own 16-label grid, as the original ui/interface.py did
piecemeal via a lazily-built render_matrix() called from three places.
"""

from __future__ import annotations

import tkinter as tk
from typing import Callable

from puzzle15.gui.theme import COLORS

SIZE = 4


class BoardGrid(tk.Frame):
    def __init__(self, parent, *, editable: bool = False, on_cell_click: Callable[[int, int], None] | None = None, **kwargs):
        super().__init__(parent, bg="#dcdde1", padx=2, pady=2, **kwargs)
        self.editable = editable
        self.on_cell_click = on_cell_click
        self._labels: list[list[tk.Label]] = []
        self._board: list[list[int | None]] = [[None] * SIZE for _ in range(SIZE)]

        for r in range(SIZE):
            row_labels = []
            for c in range(SIZE):
                label = tk.Label(self, width=5, height=2, relief="flat", font=("Segoe UI", 14, "bold"))
                label.grid(row=r, column=c, padx=2, pady=2)
                if editable:
                    label.configure(cursor="hand2")
                    label.bind("<Button-1>", lambda _event, row=r, col=c: self._handle_click(row, col))
                row_labels.append(label)
            self._labels.append(row_labels)

        self.set_board(self._board)

    def _handle_click(self, row: int, col: int) -> None:
        if self.on_cell_click:
            self.on_cell_click(row, col)

    def set_board(self, board: list[list[int | None]]) -> None:
        self._board = board
        for r in range(SIZE):
            for c in range(SIZE):
                self._render_cell(r, c, board[r][c])

    def _render_cell(self, r: int, c: int, value: int | None) -> None:
        label = self._labels[r][c]
        is_blank_like = value is None or value == -1
        text = "" if is_blank_like else str(value)
        if is_blank_like:
            bg, fg = "gray", "white"
        elif value % 2 == 0:
            bg, fg = "white", "gold"
        else:
            bg, fg = "red", "gold"
        label.configure(text=text, bg=bg, fg=fg)

    def set_cell_highlight(self, row: int, col: int, color: str | None) -> None:
        """Overlay a background color on one cell (e.g. unmatched/low-confidence
        markers in the scan review dialog). Pass None to clear it."""
        label = self._labels[row][col]
        if color is None:
            self._render_cell(row, col, self._board[row][col])
        else:
            label.configure(bg=color)

    def clear_highlights(self) -> None:
        for r in range(SIZE):
            for c in range(SIZE):
                self._render_cell(r, c, self._board[r][c])
