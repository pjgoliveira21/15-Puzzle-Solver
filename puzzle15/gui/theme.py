COLORS = {
    "primary": "#3498db",
    "secondary": "#2c3e50",
    "success": "#27ae60",
    "danger": "#e74c3c",
    "warning": "#f39c12",
    "bg": "#ffffff",
    "card": "#ffffff",
    "text": "#2f3640",
    "accent": "#9c88ff",
}


def apply_style(style) -> None:
    style.theme_use("clam")
    style.configure("TButton", font=("Segoe UI", 10), padding=5)
    style.configure("TFrame", background=COLORS["bg"])
