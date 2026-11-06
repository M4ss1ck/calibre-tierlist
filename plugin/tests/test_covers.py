"""Cover format choice: the first preferred hosted format wins, JPEG always falls back."""

from tierlist.compile import choose_format


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
