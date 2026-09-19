import tkinter as tk
from typing import Callable

from puzzle15.gui.theme import COLORS
from puzzle15.gui.widgets.buttons import make_button
from puzzle15.solver.registry import ALGORITHMS


class AlgorithmsPanel(tk.Frame):
    def __init__(self, parent, *, on_select_algorithm: Callable[[str], None], **kwargs):
        super().__init__(parent, bg=COLORS["card"], padx=15, pady=15, highlightbackground="#dcdde1", highlightthickness=1, **kwargs)

        tk.Label(self, text="ALGORITHMS", font=("Segoe UI", 11, "bold"), bg=COLORS["card"], fg=COLORS["secondary"]).pack(pady=(0, 15))
        for spec in ALGORITHMS.values():
            make_button(self, spec.label, lambda key=spec.key: on_select_algorithm(key), COLORS["secondary"]).pack(fill=tk.X, pady=5)
