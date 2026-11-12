"""Series Tiers: the Override map stored in prefs by series name, and the use cases that write it."""

from collections.abc import Iterable, Mapping
from typing import cast

from .ports import Library, Prefs

SERIES_TIER_OVERRIDES_KEY = 'series_tier_overrides'


def load_overrides(prefs: Prefs) -> dict[str, str]:
    """Every Override by series name; a missing, corrupt, or non-string entry reads as no Override at all."""
    stored = prefs.get(SERIES_TIER_OVERRIDES_KEY)
    if not isinstance(stored, Mapping):
        return {}
    entries = cast('Mapping[object, object]', stored)
    return {
        name: tier_id
        for name, tier_id in entries.items()
        if isinstance(name, str) and name and isinstance(tier_id, str) and tier_id
    }


def set_overrides(prefs: Prefs, names: Iterable[str], tier_id: str) -> None:
    """Give each of these series an Override to this Tier id, keeping every other Override."""
    overrides = load_overrides(prefs)
    overrides.update({name: tier_id for name in names if name})
    prefs.set(SERIES_TIER_OVERRIDES_KEY, overrides)


def save_overrides(prefs: Prefs, overrides: Mapping[str, str]) -> None:
    """Store the whole Override map, dropping empty names and Tier ids."""
    prefs.set(SERIES_TIER_OVERRIDES_KEY, {name: tier for name, tier in overrides.items() if name and tier})


def clear_overrides(prefs: Prefs, names: Iterable[str]) -> None:
    """Return each of these series to Auto by dropping its Override."""
    overrides = load_overrides(prefs)
    for name in names:
        overrides.pop(name, None)
    prefs.set(SERIES_TIER_OVERRIDES_KEY, overrides)


def orphans(overrides: Mapping[str, str], series_names: frozenset[str]) -> list[str]:
    """The Override series names that match no series in the library, sorted."""
    return sorted(name for name in overrides if name not in series_names)


def set_series_tier(library: Library, prefs: Prefs, book_ids: Iterable[int], tier_id: str) -> None:
    """Give every distinct series these books belong to an Override to this Tier id."""
    names = _books_series(library, book_ids)
    if names:
        set_overrides(prefs, names, tier_id)


def clear_series_tier(library: Library, prefs: Prefs, book_ids: Iterable[int]) -> None:
    """Return every series these books belong to to Auto."""
    names = _books_series(library, book_ids)
    if names:
        clear_overrides(prefs, names)


def _books_series(library: Library, book_ids: Iterable[int]) -> set[str]:
    """The distinct non-empty series names of these books."""
    values = library.read_field('series', list(book_ids))
    return {value for value in values.values() if isinstance(value, str) and value}
