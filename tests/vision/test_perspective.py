import numpy as np

from puzzle15.vision.perspective import order_vertices


def test_orders_axis_aligned_square():
    # Deliberately shuffled input order.
    points = np.array(
        [
            [100, 100],  # bottom-right
            [0, 0],  # top-left
            [100, 0],  # top-right
            [0, 100],  # bottom-left
        ],
        dtype=np.float32,
    )
    ordered = order_vertices(points)
    tl, tr, br, bl = ordered
    assert list(tl) == [0, 0]
    assert list(tr) == [100, 0]
    assert list(br) == [100, 100]
    assert list(bl) == [0, 100]


def test_orders_shuffled_trapezoid():
    top_left, top_right = [10, 10], [90, 20]
    bottom_right, bottom_left = [85, 95], [5, 80]
    # Feed the points in a shuffled order to prove this isn't a passthrough.
    points = np.array([bottom_right, top_left, bottom_left, top_right], dtype=np.float32)

    ordered = order_vertices(points)
    tl, tr, br, bl = ordered
    assert list(tl) == top_left
    assert list(tr) == top_right
    assert list(br) == bottom_right
    assert list(bl) == bottom_left
