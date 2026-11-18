"""Emblem Art: the drawing maths for one Tier's emblem, in u (the square's side over 100)."""

from collections.abc import Sequence

FONT_PX = {1: 84, 2: 58, 3: 40}


def luminance(colour: str) -> float:
    """The WCAG relative luminance of a '#rrggbb' colour."""
    red, green, blue = (_linear(channel / 255) for channel in _rgb(colour))
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def is_light(colour: str) -> bool:
    """Whether a '#rrggbb' colour is light, and so wants a dark outline."""
    return luminance(colour) > 0.179


def outline_rgb(colour: str) -> tuple[int, int, int]:
    """The outline colour: 55% of the way to black for a light Tier, to white for a dark one."""
    target = 0 if is_light(colour) else 255
    red, green, blue = (_blend(channel, target) for channel in _rgb(colour))
    return (red, green, blue)


def shown_label(graphemes: Sequence[str]) -> str:
    """The label an emblem shows: all of 1 to 3 graphemes, else the first upper-cased, else nothing."""
    if not graphemes:
        return ''
    if len(graphemes) <= 3:
        return ''.join(graphemes)
    return graphemes[0].upper()


def font_px(count: int) -> int:
    """The glyph pixel size in u for 1, 2, or 3 graphemes; other counts clamp to that range."""
    return FONT_PX[min(max(count, 1), 3)]


def glyph_scale(width: float, height: float) -> float:
    """The uniform scale that fits a glyph's bounding box inside 84 u, or 1.0 when it already does."""
    largest = max(width, height)
    return 84 / largest if largest > 84 else 1.0


def _rgb(colour: str) -> tuple[int, int, int]:
    return (int(colour[1:3], 16), int(colour[3:5], 16), int(colour[5:7], 16))


def _linear(channel: float) -> float:
    return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4


def _blend(channel: int, target: int) -> int:
    return round(channel + (target - channel) * 0.55)
