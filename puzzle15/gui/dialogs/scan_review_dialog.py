"""Review/correct a scanned grid before it becomes the initial board.

This is the dialog that actually closes the gap between the two source
projects: OpenCV template matching can misread a cell, so the user reviews
and can fix the grid before it's accepted, rather than a misread silently
becoming the puzzle's initial state.
"""

import tkinter as tk
from tkinter import simpledialog

from puzzle15.gui.dialogs._common import make_popup_header
from puzzle15.gui.theme import COLORS
from puzzle15.gui.widgets.board_grid import BoardGrid
from puzzle15.gui.widgets.buttons import make_button
from puzzle15.integration.board_conversion import BoardValidationError, scan_grid_to_board, validate_board
from puzzle15.solver.board import Board
from puzzle15.vision.result import ScanResult

LOW_CONFIDENCE_THRESHOLD = 0.65
SIZE = 4


def review_scan(parent, scan_result: ScanResult) -> Board | None:
    """Show the recognized grid for review/correction. Returns the accepted
    Board, or None if the user cancels."""
    result: dict[str, Board | None] = {"value": None}
    grid: list[list[int | None]] = [row[:] for row in scan_result.grid]

    popup = tk.Toplevel(parent)
    popup.title("Review Scanned Puzzle")
    popup.transient(parent)
    popup.grab_set()

    make_popup_header(popup, "Review Scanned Puzzle", COLORS["primary"])

    tk.Label(
        popup,
        text="Click a cell to correct it (0 = blank tile). Red = unmatched, amber = low confidence.",
        wraplength=360,
        justify="left",
        padx=20,
        pady=10,
    ).pack()

    error_label = tk.Label(popup, text="", fg=COLORS["danger"], wraplength=360, justify="left", padx=20)
    error_label.pack()

    board_container = tk.Frame(popup, pady=10)
    board_container.pack()

    def on_cell_click(row: int, col: int) -> None:
        current = grid[row][col]
        value = simpledialog.askinteger(
            "Correct cell",
            f"Value for row {row + 1}, column {col + 1} (0 = blank tile, 1-15):",
            parent=popup,
            minvalue=0,
            maxvalue=15,
            initialvalue=current if current is not None else 0,
        )
        if value is None:
            return
        grid[row][col] = None if value == 0 else value
        refresh()

    board_widget = BoardGrid(board_container, editable=True, on_cell_click=on_cell_click)
    board_widget.pack()

    def refresh() -> None:
        board_widget.set_board(grid)
        for row in range(SIZE):
            for col in range(SIZE):
                if grid[row][col] is None:
                    board_widget.set_cell_highlight(row, col, COLORS["danger"])
                    continue
                score = scan_result.scores.get((row, col))
                if score is not None and score < LOW_CONFIDENCE_THRESHOLD:
                    board_widget.set_cell_highlight(row, col, COLORS["warning"])
        error_label.configure(text="")

    refresh()

    footer = tk.Frame(popup, pady=20)
    footer.pack()

    def accept() -> None:
        try:
            board = scan_grid_to_board(grid)
            validate_board(board)
        except BoardValidationError as exc:
            error_label.configure(text=exc.message)
            return
        result["value"] = board
        popup.destroy()

    def cancel() -> None:
        popup.destroy()

    make_button(footer, "ACCEPT", accept, COLORS["success"]).pack(side=tk.LEFT, padx=5)
    make_button(footer, "CANCEL", cancel, COLORS["secondary"]).pack(side=tk.LEFT, padx=5)

    popup.wait_window()
    return result["value"]
