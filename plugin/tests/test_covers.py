"""Cover format choice, dominant colour, and the thumbnail pool."""

import time
from collections.abc import Iterable
from threading import current_thread

import pytest

from tierlist.compile import COVER_WIDTH, choose_format, cover_thumbs, dominant_colour
from tierlist.ports import Cover


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


class RecordingCovers:
    """A Covers port that records its calls and which thread served each one."""

    def __init__(self, with_cover: Iterable[int] = ()) -> None:
        self.with_cover = set(with_cover)
        self.calls: list[tuple[int, str, int]] = []
        self.threads: set[str] = set()

    def formats(self) -> frozenset[str]:
        return frozenset({'webp'})

    def cover(self, book_id: int, fmt: str, width: int) -> Cover | None:
        self.threads.add(current_thread().name)
        self.calls.append((book_id, fmt, width))
        time.sleep(0.01)  # the encode a host does, long enough that the pool has to overlap it
        return Cover(fmt, b'x', '#336699') if book_id in self.with_cover else None


def test_cover_thumbs_keeps_only_the_books_that_have_a_cover() -> None:
    covers = RecordingCovers(with_cover={2, 3})

    thumbs = cover_thumbs(covers, [1, 2, 3, 4], 'webp', COVER_WIDTH)

    assert list(thumbs) == [2, 3]


def test_cover_thumbs_asks_for_the_chosen_format_and_width() -> None:
    covers = RecordingCovers({1})

    cover_thumbs(covers, [1], 'avif', 120)

    assert covers.calls == [(1, 'avif', 120)]


def test_cover_thumbs_encodes_on_more_than_one_thread() -> None:
    covers = RecordingCovers(range(32))

    cover_thumbs(covers, range(32), 'webp', COVER_WIDTH)

    assert len(covers.threads) > 1


def test_cover_thumbs_raises_when_a_host_cannot_encode() -> None:
    class Broken(RecordingCovers):
        def cover(self, book_id: int, fmt: str, width: int) -> Cover | None:
            raise RuntimeError('no codec for webp')

    with pytest.raises(RuntimeError, match='no codec'):
        cover_thumbs(Broken(), [1, 2], 'webp', COVER_WIDTH)
