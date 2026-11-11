"""Cover thumbnails: the formats the board can show, how to pick one, and its dominant colour."""

from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor

from ..ports import Cover, Covers

COVER_WIDTH = 240
FORMATS = ('avif', 'webp', 'jpeg')
EMPTY_COLOUR = '#808080'
COVER_WORKERS = 8


def choose_format(available: Iterable[str]) -> str:
    """The first preferred format this host can encode, or JPEG when none match."""
    present = set(available)
    return next((fmt for fmt in FORMATS if fmt in present), 'jpeg')


def cover_thumbs(covers: Covers, book_ids: Iterable[int], fmt: str, width: int) -> dict[int, Cover]:
    """Every thumbnail these books have, by id, encoded on a small pool.

    Encoding dominates a compile on libraries with covers, and the encoders release the GIL, so overlapping
    them is most of the win; a failing host raises here, as it would have walked in order.
    """
    ids = list(book_ids)

    def thumb(book_id: int) -> Cover | None:
        return covers.cover(book_id, fmt, width)

    with ThreadPoolExecutor(max_workers=min(COVER_WORKERS, max(1, len(ids)))) as pool:
        shots = pool.map(thumb, ids)
        return {book_id: cover for book_id, cover in zip(ids, shots, strict=True) if cover is not None}


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
