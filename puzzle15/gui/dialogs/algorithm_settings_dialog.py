import tkinter as tk
from dataclasses import dataclass

from puzzle15.gui.dialogs._common import make_popup_header
from puzzle15.gui.theme import COLORS
from puzzle15.gui.widgets.buttons import make_button
from puzzle15.solver.registry import DEFAULT_MAX_DEPTH, DEFAULT_TIMEOUT, AlgorithmSpec


@dataclass
class AlgorithmSettings:
    timeout: float
    max_depth: int = DEFAULT_MAX_DEPTH


def ask_algorithm_settings(parent, spec: AlgorithmSpec) -> AlgorithmSettings | None:
    """Modal popup to configure timeout (and max depth, for DFS). Returns
    None if cancelled."""
    result: dict[str, AlgorithmSettings | None] = {"value": None}

    popup = tk.Toplevel(parent)
    popup.title(f"Configure {spec.label}")
    popup.transient(parent)
    popup.grab_set()

    make_popup_header(popup, f"Configure {spec.label}", COLORS["primary"])

    form = tk.Frame(popup, padx=30, pady=20)
    form.pack(fill=tk.BOTH)

    timeout_var = tk.IntVar(value=DEFAULT_TIMEOUT)
    depth_var = tk.IntVar(value=DEFAULT_MAX_DEPTH)

    tk.Label(form, text="Timeout (s):").pack(anchor="w")
    tk.Entry(form, textvariable=timeout_var).pack(fill=tk.X, pady=5)

    if spec.supports_max_depth:
        tk.Label(form, text="Max depth:").pack(anchor="w")
        tk.Entry(form, textvariable=depth_var).pack(fill=tk.X, pady=5)

    def start() -> None:
        result["value"] = AlgorithmSettings(timeout=timeout_var.get(), max_depth=depth_var.get())
        popup.destroy()

    make_button(form, "START", start, COLORS["success"]).pack(fill=tk.X, pady=10)

    popup.wait_window()
    return result["value"]
