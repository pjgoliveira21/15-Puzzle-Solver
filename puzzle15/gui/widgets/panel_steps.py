"""Easy mode's third panel: one Solve button, then step-by-step playback.

Unlike Advanced mode's result dialog (raw stats + a one-shot "play all"
animation), this stays in the panel and lets the user step through at
their own pace with a plain-language instruction per move - the shape
this is meant to grow into once live camera guidance exists (Roadmap
Stage D/E in the project plan).
"""

import tkinter as tk
from typing import Callable

from puzzle15.gui.theme import COLORS
from puzzle15.gui.widgets.board_grid import BoardGrid
from puzzle15.gui.widgets.buttons import make_button
from puzzle15.solver.moves import MoveInstruction, describe_moves
from puzzle15.solver.result import SolveResult

STATE_READY = "ready"
STATE_SOLVED = "solved"
STATE_FAILED = "failed"

FAILURE_MESSAGE = (
    "No solution found within the default time limit. Switch to Advanced "
    "mode to try a different algorithm or a longer timeout."
)


class StepsPanel(tk.Frame):
    def __init__(self, parent, *, on_solve: Callable[[], None], **kwargs):
        super().__init__(parent, bg=COLORS["card"], padx=15, pady=15, highlightbackground="#dcdde1", highlightthickness=1, **kwargs)

        tk.Label(self, text="SOLVE", font=("Segoe UI", 11, "bold"), bg=COLORS["card"], fg=COLORS["secondary"]).pack(pady=(0, 15))

        self._instructions: list[MoveInstruction] = []
        self._path: list = []
        self._step = 0

        self.solve_button = make_button(self, "Solve", on_solve, COLORS["success"])
        self.message_label = tk.Label(self, text=FAILURE_MESSAGE, bg=COLORS["card"], fg=COLORS["danger"], wraplength=220, justify="left")
        self.board_widget = BoardGrid(self)
        self.step_label = tk.Label(self, text="", bg=COLORS["card"], fg=COLORS["text"], font=("Segoe UI", 10, "bold"), wraplength=220, justify="left")

        self._nav_frame = tk.Frame(self, bg=COLORS["card"])
        self.prev_button = make_button(self._nav_frame, "◀ Prev", self._show_prev, COLORS["secondary"])
        self.next_button = make_button(self._nav_frame, "Next ▶", self._show_next, COLORS["secondary"])
        self.prev_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        self.next_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

        self.reset_to_ready()

    def reset_to_ready(self) -> None:
        self._instructions = []
        self._path = []
        self._step = 0
        self._set_state(STATE_READY)

    def show_result(self, result: SolveResult) -> None:
        if not result.success or not result.path:
            self._set_state(STATE_FAILED)
            return
        self._path = result.path
        self._instructions = describe_moves(result.path)
        self._step = 0
        self._set_state(STATE_SOLVED)

    def _set_state(self, state: str) -> None:
        for widget in (self.solve_button, self.message_label, self.board_widget, self.step_label, self._nav_frame):
            widget.pack_forget()

        if state == STATE_READY:
            self.solve_button.pack(fill=tk.X, pady=5)
        elif state == STATE_FAILED:
            self.message_label.pack(fill=tk.X, pady=10)
        elif state == STATE_SOLVED:
            self.board_widget.pack(pady=10)
            self.step_label.pack(fill=tk.X, pady=5)
            self._nav_frame.pack(fill=tk.X, pady=5)
            self._render_step()

    def _render_step(self) -> None:
        self.board_widget.set_board(self._path[self._step])
        total_moves = len(self._instructions)
        if self._step < total_moves:
            move = self._instructions[self._step]
            self.step_label.configure(text=f"Step {self._step + 1} of {total_moves}: move tile {move.tile} {move.direction}")
            self.board_widget.set_cell_highlight(move.from_pos[0], move.from_pos[1], COLORS["accent"])
        else:
            self.step_label.configure(text="Solved!")
        self.prev_button.configure(state=tk.NORMAL if self._step > 0 else tk.DISABLED)
        self.next_button.configure(state=tk.NORMAL if self._step < total_moves else tk.DISABLED)

    def _show_prev(self) -> None:
        if self._step > 0:
            self._step -= 1
            self._render_step()

    def _show_next(self) -> None:
        if self._step < len(self._instructions):
            self._step += 1
            self._render_step()
