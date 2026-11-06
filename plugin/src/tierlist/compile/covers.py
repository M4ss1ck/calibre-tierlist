"""Cover thumbnails: the formats the board can show and how to pick one."""

from collections.abc import Iterable
from dataclasses import dataclass

COVER_WIDTH = 240
FORMATS = ('avif', 'webp', 'jpeg')


@dataclass(frozen=True)
class Cover:
    """One book's cover thumbnail: its image format, bytes, and dominant colour ('#rrggbb')."""

    format: str
    data: bytes
    colour: str


def choose_format(available: Iterable[str]) -> str:
    """The first preferred format this host can encode, or JPEG when none match."""
    present = set(available)
    return next((fmt for fmt in FORMATS if fmt in present), 'jpeg')
