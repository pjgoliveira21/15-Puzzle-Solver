import tkinter as tk

from puzzle15.gui.dialogs._common import make_popup_header
from puzzle15.gui.theme import COLORS
from puzzle15.gui.widgets.buttons import make_button

DIFFICULTIES = [("Easy", "easy"), ("Normal", "normal"), ("Hard", "hard")]


def ask_difficulty(parent) -> str | None:
    """Modal popup to pick a shuffle difficulty. Returns the difficulty key, or None if cancelled."""
    result: dict[str, str | None] = {"value": None}

    popup = tk.Toplevel(parent)
    popup.title("Difficulty")
    popup.transient(parent)
    popup.grab_set()

    make_popup_header(popup, "Difficulty", COLORS["accent"])

    body = tk.Frame(popup, pady=20, padx=20)
    body.pack()

    def choose(key: str) -> None:
        result["value"] = key
        popup.destroy()

    for label, key in DIFFICULTIES:
        make_button(body, label, lambda k=key: choose(k), COLORS["secondary"]).pack(pady=5, fill=tk.X)

    popup.wait_window()
    return result["value"]
