import tkinter as tk
from tkinter import ttk

from puzzle15.gui.dialogs._common import make_popup_header
from puzzle15.gui.theme import COLORS


class ProgressDialog:
    """A plain indeterminate-progress popup. No knowledge of what it's
    waiting on - the caller closes it via .close() when done."""

    def __init__(self, parent, message: str, title: str = "Working"):
        self.popup = tk.Toplevel(parent)
        self.popup.title(title)
        self.popup.transient(parent)
        self.popup.grab_set()
        self.popup.resizable(False, False)

        make_popup_header(self.popup, title, COLORS["secondary"])

        container = tk.Frame(self.popup, pady=20, padx=20)
        container.pack(fill=tk.BOTH)
        tk.Label(container, text=message).pack(pady=10)

        self.progressbar = ttk.Progressbar(container, mode="indeterminate", length=200)
        self.progressbar.pack(pady=10)
        self.progressbar.start()

    def close(self) -> None:
        if self.popup.winfo_exists():
            self.popup.destroy()
