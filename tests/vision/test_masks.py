from puzzle15.vision.masks import load_digit_masks


def test_loads_all_fifteen_masks():
    masks = load_digit_masks()
    assert set(masks.keys()) == set(range(1, 16))


def test_masks_are_valid_images():
    masks = load_digit_masks()
    for number, image in masks.items():
        assert image is not None, f"mask {number} failed to load"
        assert image.ndim == 2  # loaded grayscale
