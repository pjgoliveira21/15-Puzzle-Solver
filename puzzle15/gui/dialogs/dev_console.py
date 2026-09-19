"""Non-modal popup streaming the captured debug logs (solver/vision internals).

Polls the log buffer on a timer rather than appending directly from log
calls, since those can happen on the background solve/scan threads and
Tkinter widgets may only be touched from the main thread.
"""

import tkinter as tk
from tkinter import scrolledtext

from puzzle15.gui.logging_support import BufferingLogHandler
from puzzle15.gui.theme import COLORS
from puzzle15.gui.widgets.buttons import make_button

POLL_INTERVAL_MS = 300


class DevConsole:
    def __init__(self, parent, log_handler: BufferingLogHandler):
        self.log_handler = log_handler
        self._rendered_count = 0
        self._closed = False

        self.window = tk.Toplevel(parent)
        self.window.title("Dev Console")
        self.window.geometry("700x400")
        self.window.protocol("WM_DELETE_WINDOW", self.close)

        header = tk.Frame(self.window, bg=COLORS["secondary"], pady=10)
        header.pack(fill=tk.X)
        tk.Label(header, text="Dev Console", fg="white", bg=COLORS["secondary"], font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT, padx=10)
        make_button(header, "Clear", self._clear, COLORS["danger"]).pack(side=tk.RIGHT, padx=10)

        self.text = scrolledtext.ScrolledText(self.window, state="disabled", font=("Consolas", 9), bg="#1e1e1e", fg="#d4d4d4", wrap="none")
        self.text.pack(fill=tk.BOTH, expand=True)

        self._render_backlog()
        self._poll()

    def _render_backlog(self) -> None:
        for line in self.log_handler.lines:
            self._append(line)
        self._rendered_count = len(self.log_handler.lines)

    def _append(self, line: str) -> None:
        self.text.configure(state="normal")
        self.text.insert(tk.END, line + "\n")
        self.text.see(tk.END)
        self.text.configure(state="disabled")

    def _poll(self) -> None:
        if self._closed or not self.window.winfo_exists():
            return
        lines = self.log_handler.lines
        if len(lines) > self._rendered_count:
            for line in lines[self._rendered_count :]:
                self._append(line)
            self._rendered_count = len(lines)
        self.window.after(POLL_INTERVAL_MS, self._poll)

    def _clear(self) -> None:
        self.log_handler.lines.clear()
        self._rendered_count = 0
        self.text.configure(state="normal")
        self.text.delete("1.0", tk.END)
        self.text.configure(state="disabled")

    def focus(self) -> None:
        self.window.lift()
        self.window.focus_force()

    def close(self) -> None:
        self._closed = True
        if self.window.winfo_exists():
            self.window.destroy()
