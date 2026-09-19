"""Shared helpers for dialog popups."""

import tkinter as tk


def make_popup_header(popup: tk.Toplevel, title: str, color: str) -> tk.Frame:
    header = tk.Frame(popup, bg=color, pady=15)
    header.pack(fill=tk.X)
    tk.Label(header, text=title, fg="white", bg=color, font=("Segoe UI", 12, "bold")).pack()
    return header
