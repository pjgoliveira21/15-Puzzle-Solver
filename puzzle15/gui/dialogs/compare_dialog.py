"""Advanced mode's Compare Algorithms dialogs: a timeout prompt, then a
results table."""

import math
import tkinter as tk
from tkinter import ttk

from puzzle15.gui.dialogs._common import make_popup_header
from puzzle15.gui.theme import COLORS
from puzzle15.gui.widgets.buttons import make_button
from puzzle15.solver.registry import ALGORITHMS, DEFAULT_TIMEOUT
from puzzle15.solver.result import SolveResult

COLUMNS = ("algorithm", "success", "time", "steps", "explored", "speed")
HEADINGS = {
    "algorithm": "Algorithm",
    "success": "Success",
    "time": "Time (s)",
    "steps": "Steps",
    "explored": "Explored",
    "speed": "Speed (nps)",
}


def ask_comparison_timeout(parent) -> float | None:
    """Modal popup to set the per-algorithm timeout before comparing.
    Returns None if cancelled."""
    result: dict[str, float | None] = {"value": None}

    popup = tk.Toplevel(parent)
    popup.title("Compare Algorithms")
    popup.transient(parent)
    popup.grab_set()

    make_popup_header(popup, "Compare Algorithms", COLORS["primary"])

    form = tk.Frame(popup, padx=30, pady=20)
    form.pack(fill=tk.BOTH)

    tk.Label(form, text="Timeout per algorithm (s):").pack(anchor="w")
    timeout_var = tk.StringVar(value=str(DEFAULT_TIMEOUT))
    tk.Entry(form, textvariable=timeout_var).pack(fill=tk.X, pady=5)

    error_label = tk.Label(form, text="", fg=COLORS["danger"])
    error_label.pack(anchor="w")

    def start() -> None:
        try:
            value = float(timeout_var.get())
        except ValueError:
            error_label.configure(text="Enter a number.")
            return
        # timeout=0 means "no timeout" to the search implementations
        # (`if timeout and ...`), and so does NaN/inf (the elapsed-time
        # check never exceeds it) - float() accepts "nan"/"inf" strings,
        # so both must be rejected explicitly alongside <= 0.
        if not math.isfinite(value) or value <= 0:
            error_label.configure(text="Timeout must be a positive number.")
            return
        result["value"] = value
        popup.destroy()

    make_button(form, "RUN", start, COLORS["success"]).pack(fill=tk.X, pady=10)

    popup.wait_window()
    return result["value"]


def show_comparison_results(parent, results: dict[str, SolveResult]) -> None:
    popup = tk.Toplevel(parent)
    popup.title("Comparison Results")
    popup.geometry("650x350")
    popup.grab_set()

    make_popup_header(popup, "Comparison Results", COLORS["primary"])

    tree = ttk.Treeview(popup, columns=COLUMNS, show="headings", height=len(results))
    for col in COLUMNS:
        tree.heading(col, text=HEADINGS[col])
        tree.column(col, anchor="center", width=100)

    for key, result in results.items():
        nps = result.explored / result.time_seconds if result.time_seconds > 0 else 0
        tree.insert(
            "",
            tk.END,
            values=(
                ALGORITHMS[key].label,
                "Yes" if result.success else "No",
                result.time_seconds,
                result.steps if result.success else "-",
                f"{result.explored:,}",
                f"{nps:,.0f}",
            ),
        )

    tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    make_button(popup, "CLOSE", popup.destroy, COLORS["secondary"]).pack(side=tk.BOTTOM, pady=20, padx=20, fill=tk.X)
