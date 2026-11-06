"""Cover format choice and dominant colour."""

from tierlist.compile import choose_format, dominant_colour


def test_prefers_avif_when_the_host_can_encode_it() -> None:
    assert choose_format({'avif', 'webp', 'jpeg'}) == 'avif'


def test_prefers_webp_over_jpeg() -> None:
    assert choose_format({'webp', 'jpeg'}) == 'webp'


def test_uses_jpeg_when_it_is_the_only_preferred_format() -> None:
    assert choose_format({'jpeg'}) == 'jpeg'


def test_falls_back_to_jpeg_when_the_host_encodes_no_preferred_format() -> None:
    assert choose_format(set()) == 'jpeg'


def test_falls_back_to_jpeg_for_unknown_only_formats() -> None:
    assert choose_format({'png'}) == 'jpeg'


def test_dominant_colour_of_a_solid_fill_is_that_colour() -> None:
    assert dominant_colour([(18, 52, 86)] * 64) == '#123456'


def test_dominant_colour_returns_black_for_a_mostly_black_image() -> None:
    pixels = [(0, 0, 0)] * 200 + [(255, 255, 255)] * 56

    assert dominant_colour(pixels) == '#000000'


def test_dominant_colour_of_no_pixels_is_grey() -> None:
    assert dominant_colour([]) == '#808080'


def test_dominant_colour_breaks_ties_by_the_bucket_seen_first() -> None:
    assert dominant_colour([(255, 0, 0), (0, 255, 0)]) == '#ff0000'
