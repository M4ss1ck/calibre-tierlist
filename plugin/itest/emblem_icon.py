"""Integration test for the emblem icon: a transparent PNG of a Tier's label, in its colours.

Run with ``calibre-debug -e plugin/itest/emblem_icon.py`` after installing the zip into a
throwaway ``CALIBRE_CONFIG_DIRECTORY``. Prints ``EMBLEM ICON OK`` and exits 0 on success.
calibre runs Python with -OO, which strips ``assert``; use ``expect``.
"""

import sys
from collections.abc import Iterator

from calibre.gui2 import Application
from calibre_plugins.tierlist.calibre_ui.emblem_icon import SIDE, emblem_png
from calibre_plugins.tierlist.emblem_art import is_light, outline_rgb
from calibre_plugins.tierlist.tiers import DEFAULT_TIER_CONFIG, Tier
from qt.core import QColor, QImage

EDGE = 6  # pixels (0, 0) to (5, 5): the first 2 u of the square
CENTRE_GAP = 6  # px the drawn centre may sit off the middle of the square
FILL = (160, SIDE)  # px the drawn glyph spans: a capital (about 0.7 em of 84 u) plus its outline, at most the side


def expect(ok: bool, message: object) -> None:
    if not ok:
        raise SystemExit(f'EMBLEM ICON FAIL: {message}')


def decode(tier: Tier) -> QImage:
    """The Tier's emblem, decoded, after checking its raster and that it carries alpha."""
    image = QImage.fromData(emblem_png(tier), 'PNG')
    expect(not image.isNull(), f'{tier.id}: the PNG does not decode')
    expect((image.width(), image.height()) == (SIDE, SIDE), f'{tier.id}: {image.width()}x{image.height()}')
    expect(image.hasAlphaChannel(), f'{tier.id}: no alpha channel')
    return image


def drawn(image: QImage) -> Iterator[tuple[int, int, QColor]]:
    """The position and colour of every pixel that carries any opacity."""
    for x in range(SIDE):
        for y in range(SIDE):
            pixel = image.pixelColor(x, y)
            if pixel.alpha():
                yield x, y, pixel


def rgb(colour: QColor) -> tuple[int, int, int]:
    return (colour.red(), colour.green(), colour.blue())


def colours(image: QImage) -> set[tuple[int, int, int]]:
    """The colours of the image's fully opaque pixels."""
    return {rgb(pixel) for _, _, pixel in drawn(image) if pixel.alpha() == 255}


def bounds(image: QImage) -> tuple[int, int, int, int]:
    """The left, top, right and bottom of what the image drew."""
    points = [(x, y) for x, y, _ in drawn(image)]
    return min(x for x, _ in points), min(y for _, y in points), max(x for x, _ in points), max(y for _, y in points)


def check_tier(tier: Tier) -> None:
    """A default Tier's emblem: clear corners, its colours, and a glyph centred and nearly filling the square."""
    image = decode(tier)
    expect(not any(image.pixelColor(x, y).alpha() for x in range(EDGE) for y in range(EDGE)), f'{tier.id}: corners')
    found = colours(image)
    expect(rgb(QColor(tier.colour)) in found, f'{tier.id}: no pixel of the Tier colour')
    expect(outline_rgb(tier.colour) in found, f'{tier.id}: no pixel of the outline colour')
    left, top, right, bottom = bounds(image)
    centre = ((left + right) / 2, (top + bottom) / 2)
    expect(all(abs(axis - SIDE / 2) <= CENTRE_GAP for axis in centre), f'{tier.id}: centre shows at {centre}')
    largest = max(right - left, bottom - top) + 1
    expect(FILL[0] <= largest <= FILL[1], f'{tier.id}: the glyph spans {largest} px')


def check_other_tiers() -> None:
    """A label over three graphemes draws its first letter, and a dark Tier gets a light outline."""
    expect(bool(bounds(decode(Tier('m', 'Masterpiece', '#ffbf7f')))), 'the Masterpiece label drew nothing')
    dark = Tier('dark', 'X', '#202020')
    expect(not is_light(dark.colour), f'{dark.colour} is light')
    expect(outline_rgb(dark.colour) in colours(decode(dark)), f'{dark.colour} has no light outline pixel')


def check_blank_label() -> None:
    """An empty or whitespace label gives a fully transparent PNG."""
    for label in ('', '   '):
        expect(not list(drawn(decode(Tier('blank', label, '#ff7f7f')))), f'a {label!r} label drew something')


def main() -> int:
    Application([])
    for tier in DEFAULT_TIER_CONFIG.tiers:
        check_tier(tier)
    check_other_tiers()
    check_blank_label()
    print('EMBLEM ICON OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
