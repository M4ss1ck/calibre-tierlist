"""Lane Order: the reader's hand-set order of the Stacks and Cards inside each Lane."""

from collections.abc import Mapping, Sequence
from typing import cast

from .ports import Prefs

LANE_ORDER_KEY = 'lane_order'
UNRANKED_LANE = 'unranked'

Place = tuple[str, str | int]


def load_order(prefs: Prefs) -> dict[str, list[Place]]:
    """Every Lane's stored places, by Lane key; a missing, corrupt, or empty entry reads as no order."""
    stored = prefs.get(LANE_ORDER_KEY)
    if not isinstance(stored, Mapping):
        return {}
    entries = cast('Mapping[object, object]', stored)
    order: dict[str, list[Place]] = {}
    for lane, items in entries.items():
        if not isinstance(lane, str) or not lane or not isinstance(items, list):
            continue
        places = [place for item in cast('list[object]', items) if (place := place_from_dict(item)) is not None]
        if places:
            order[lane] = places
    return order


def save_order(prefs: Prefs, order: Mapping[str, Sequence[Place]]) -> None:
    """Store each Lane's places in order, dropping empty Lanes."""
    prefs.set(
        LANE_ORDER_KEY,
        {lane: [{kind: key} for kind, key in places] for lane, places in order.items() if lane and places},
    )


def prune(prefs: Prefs, series_names: frozenset[str], book_ids: frozenset[int]) -> None:
    """Drop stored places naming no current series or book, then save the rest."""
    order = load_order(prefs)
    if not order:
        return
    save_order(
        prefs,
        {lane: [place for place in places if _exists(place, series_names, book_ids)] for lane, places in order.items()},
    )


def place_from_dict(item: object) -> Place | None:
    """One stored place, or None when its shape is not a series name or a book id."""
    if not isinstance(item, Mapping):
        return None
    entry = cast('Mapping[object, object]', item)
    series = entry.get('series')
    if isinstance(series, str) and series:
        return ('series', series)
    book = entry.get('book')
    if isinstance(book, int) and not isinstance(book, bool):
        return ('book', book)
    return None


def _exists(place: Place, series_names: frozenset[str], book_ids: frozenset[int]) -> bool:
    kind, key = place
    return key in series_names if kind == 'series' else key in book_ids
