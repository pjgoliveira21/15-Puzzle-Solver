"""Shared button styling factory.

Replaces the original PuzzleApp._custom_btn method: dialogs used to reach
back into the app instance just to build a styled button. A standalone
function needs no reference to the app at all.
"""

import tkinter as tk


def make_button(parent, text: str, command, color: str) -> tk.Button:
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=color,
        fg="white",
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        cursor="hand2",
        activebackground=color,
        pady=8,
    )
