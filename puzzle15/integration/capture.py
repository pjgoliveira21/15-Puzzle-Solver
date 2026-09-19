"""Seam for choosing a photo source for Scan Photo.

Today this is just a file picker. A future webcam-capture function can
implement the same `Path | None` contract and be swapped in here without
ScanService, review_scan, or any panel needing to change (Roadmap Stage B
in the project plan).
"""

from __future__ import annotations

from pathlib import Path
from tkinter import filedialog


def choose_photo_source(parent) -> Path | None:
    path = filedialog.askopenfilename(parent=parent, filetypes=[("Images", "*.jpg *.jpeg *.png")])
    if not path:
        return None
    return Path(path)
