"""Emblem Art: the drawing maths for the frozen design, version 1."""

import pytest

from tierlist.emblem_art import font_px, glyph_scale, is_light, luminance, outline_rgb, shown_label

LIGHT_COLOURS = ('#ff7f7f', '#ffbf7f', '#ffdf7f', '#ffff7f', '#bfff7f', '#7fbfff')


@pytest.mark.parametrize('colour', LIGHT_COLOURS)
def test_every_default_tier_colour_is_light(colour: str) -> None:
    assert is_light(colour)


def test_luminance_spans_black_to_white() -> None:
    assert luminance('#000000') == pytest.approx(0.0)
    assert luminance('#ffffff') == pytest.approx(1.0)


@pytest.mark.parametrize(('colour', 'light'), [('#777777', True), ('#707070', False), ('#000000', False)])
def test_is_light_splits_on_luminance(colour: str, light: bool) -> None:
    assert is_light(colour) is light


def test_outline_of_a_light_colour_is_dark() -> None:
    assert outline_rgb('#ff7f7f') == (115, 57, 57)


def test_outline_of_a_dark_colour_is_light() -> None:
    assert outline_rgb('#336699') == (163, 186, 209)


@pytest.mark.parametrize(
    ('graphemes', 'shown'),
    [
        ((), ''),
        (('S',), 'S'),
        (('S', 'A'), 'SA'),
        (('A', 'B', 'C'), 'ABC'),
        (('s', 'a', 'b', 'c'), 'S'),
        (('M', 'a', 's', 't'), 'M'),
    ],
)
def test_shown_label(graphemes: tuple[str, ...], shown: str) -> None:
    assert shown_label(graphemes) == shown


@pytest.mark.parametrize(('count', 'px'), [(1, 84), (2, 58), (3, 40)])
def test_font_px(count: int, px: int) -> None:
    assert font_px(count) == px


@pytest.mark.parametrize(
    ('width', 'height', 'scale'),
    [(84.0, 50.0, 1.0), (50.0, 84.0, 1.0), (100.0, 50.0, 0.84), (168.0, 40.0, 0.5)],
)
def test_glyph_scale(width: float, height: float, scale: float) -> None:
    assert glyph_scale(width, height) == pytest.approx(scale)
