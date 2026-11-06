"""Cover thumbnails: the formats the board can show, how to pick one, and its dominant colour."""

from collections.abc import Iterable

COVER_WIDTH = 240
FORMATS = ('avif', 'webp', 'jpeg')
EMPTY_COLOUR = '#808080'


def choose_format(available: Iterable[str]) -> str:
    """The first preferred format this host can encode, or JPEG when none match."""
    present = set(available)
    return next((fmt for fmt in FORMATS if fmt in present), 'jpeg')


def dominant_colour(pixels: Iterable[tuple[int, int, int]]) -> str:
    """The most common colour in these RGB pixels, as '#rrggbb'; grey when there are none."""
    buckets: dict[tuple[int, int, int], list[tuple[int, int, int]]] = {}
    for pixel in pixels:
        key = (pixel[0] >> 5, pixel[1] >> 5, pixel[2] >> 5)
        buckets.setdefault(key, []).append(pixel)
    if not buckets:
        return EMPTY_COLOUR
    best = max(buckets.values(), key=len)
    size = len(best)
    red = round(sum(pixel[0] for pixel in best) / size)
    green = round(sum(pixel[1] for pixel in best) / size)
    blue = round(sum(pixel[2] for pixel in best) / size)
    return f'#{red:02x}{green:02x}{blue:02x}'
