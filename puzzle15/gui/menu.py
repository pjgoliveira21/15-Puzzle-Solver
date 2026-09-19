"""Native Tk menu bar: View (mode switch), Tools (Dev Console), Help (About).

Replaces the old top-bar Dev Console button, which left an awkward empty
strip above the panels once nothing else lived up there.
"""

import tkinter as tk
from tkinter import messagebox
from typing import Callable

ABOUT_TEXT = (
    "15-Puzzle Solver\n\n"
    "Solves the 15-puzzle from a manually entered/generated board, or from "
    "a photo of a physical puzzle, using search algorithms and OpenCV "
    "recognition merged from the original 15-Puzzle-AI-Solver and "
    "15-Puzzle-Reader projects."
)


def build_menu_bar(
    root: tk.Tk,
    *,
    mode_var: tk.StringVar,
    on_mode_change: Callable[[], None],
    on_toggle_dev_console: Callable[[], None],
) -> None:
    menu_bar = tk.Menu(root)

    view_menu = tk.Menu(menu_bar, tearoff=False)
    view_menu.add_radiobutton(label="Easy", variable=mode_var, value="easy", command=on_mode_change)
    view_menu.add_radiobutton(label="Advanced", variable=mode_var, value="advanced", command=on_mode_change)
    menu_bar.add_cascade(label="View", menu=view_menu)

    tools_menu = tk.Menu(menu_bar, tearoff=False)
    tools_menu.add_command(label="Dev Console", command=on_toggle_dev_console)
    menu_bar.add_cascade(label="Tools", menu=tools_menu)

    help_menu = tk.Menu(menu_bar, tearoff=False)
    help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", ABOUT_TEXT))
    menu_bar.add_cascade(label="Help", menu=help_menu)

    root.configure(menu=menu_bar)
