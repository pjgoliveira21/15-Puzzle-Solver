"""Matplotlib debug visualization of the scan pipeline's intermediate steps.

Optional: only imported by debug_cli.py, and only needs matplotlib
(the `debug`/`dev` extras), never the GUI or the core scan pipeline.
"""

import cv2
import matplotlib.pyplot as plt
import numpy as np


def _grid_cells_image(target_size, cell_size, cells_processed):
    image = np.ones((target_size[0] + 30, target_size[1] + 30, 3), dtype=np.uint8) * 255
    margin = 4
    for (row, col), cell in cells_processed.items():
        if cell is not None:
            y = row * (cell_size + margin)
            x = col * (cell_size + margin)
            image[y : y + cell.shape[0], x : x + cell.shape[1]] = (
                cv2.cvtColor(cell, cv2.COLOR_GRAY2BGR) if len(cell.shape) == 2 else cell
            )
    return image


def _grid_text_image(target_size, cell_size, grid):
    image = np.ones((target_size[0] + 30, target_size[1] + 30, 3), dtype=np.uint8) * 255
    for row in range(4):
        for col in range(4):
            number = grid[row][col] if grid[row][col] else -1
            y = row * cell_size + cell_size // 2
            x = col * cell_size + cell_size // 2
            cv2.putText(image, str(number), (x - 20, y + 20), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
    return image


def _warped_with_grid_image(warped, cell_size, grid):
    image = warped.copy()
    for row in range(4):
        for col in range(4):
            y1, y2 = row * cell_size, (row + 1) * cell_size
            x1, x2 = col * cell_size, (col + 1) * cell_size
            number = grid[row][col]
            if number is not None:
                cv2.putText(image, str(number), (x1 + 40, y1 + 85), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    return image


def show_scan_debug_plots(original, binary_mask, warped, lines_image, numbers_segmented, target_size, cell_size, cells_processed, grid):
    grid_cells = _grid_cells_image(target_size, cell_size, cells_processed)
    grid_text = _grid_text_image(target_size, cell_size, grid)
    warped_with_grid = _warped_with_grid_image(warped, cell_size, grid)

    panels = [
        (cv2.cvtColor(original, cv2.COLOR_BGR2RGB), "Original"),
        (binary_mask, "Segmented"),
        (cv2.cvtColor(lines_image, cv2.COLOR_BGR2RGB), "Detected Edges"),
        (cv2.cvtColor(warped, cv2.COLOR_BGR2RGB), "Top-down View"),
        (cv2.cvtColor(numbers_segmented, cv2.COLOR_BGR2RGB), "Digits Segmented"),
        (cv2.cvtColor(grid_cells, cv2.COLOR_BGR2RGB), "Cell Grid"),
        (cv2.cvtColor(warped_with_grid, cv2.COLOR_BGR2RGB), "Labeled Cells"),
        (cv2.cvtColor(grid_text, cv2.COLOR_BGR2RGB), "Output Grid"),
    ]

    plt.figure(figsize=(10, 10))
    for index, (image, title) in enumerate(panels, start=1):
        plt.subplot(2, 4, index)
        plt.imshow(image, cmap="gray")
        plt.axis("off")
        plt.title(title)
    plt.show()
