"""Series Stacks: the ordered positions one series occupies on the board."""

from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date

from ..lane_order import Place
from ..tiers import Tier, TierConfig
from .covers import EMPTY_COLOUR

Rank = tuple[date | None, str, int]


@dataclass(frozen=True)
class Position:
    """One position in a Stack: the number a reader sees, and the owned book id or None for a Placeholder."""

    number: str
    book: int | None


@dataclass(frozen=True)
class Series:
    """One series on the board: its Placeholder colour, every position, and whether it is an Override."""

    colour: str
    positions: tuple[Position, ...]
    override: bool


@dataclass(frozen=True)
class SeriesTier:
    """The Tier a series is shown in, and whether that Tier comes from an Override."""

    tier_id: str | None
    override: bool


def build_series(
    indexes: Mapping[int, object | None],
    totals: Iterable[object | None],
    colours: Mapping[int, str],
    override: bool,
) -> Series:
    """Build the Stack for one series from each member's series index and colour."""
    owned = {book: _index(index) for book, index in indexes.items()}
    ordered = _positions(owned, _end(owned, _total(totals)))
    return Series(
        _colour(ordered, colours),
        tuple(Position(display_number(index), book) for index, book in ordered),
        override,
    )


def ordered_lane(present: Mapping[Place, Rank], stored: Iterable[Place]) -> list[Place]:
    """The Lane's places: stored ones first in stored order, then unplaced ones by date read, undated last,
    then name or title, then id."""
    known = set(present)
    placed: list[Place] = []
    seen: set[Place] = set()
    for place in stored:
        if place in known and place not in seen:
            placed.append(place)
            seen.add(place)
    fresh = sorted((place for place in present if place not in seen), key=lambda place: _lane_key(present[place]))
    return [*placed, *fresh]


def auto_tier(tier_ids: Iterable[str | None], tiers: tuple[Tier, ...]) -> str | None:
    """The most common Book Tier among these ids, ties going to the lower Tier; None when none is ranked."""
    order = {tier.id: index for index, tier in enumerate(tiers)}
    counts = Counter(tier_id for tier_id in tier_ids if tier_id is not None)
    return max(counts, key=lambda tier_id: (counts[tier_id], order[tier_id])) if counts else None


def series_tier(
    name: str, tier_ids: Iterable[str | None], config: TierConfig, overrides: Mapping[str, str]
) -> SeriesTier:
    """This series' Series Tier and whether it is an Override: an Override naming a missing Tier falls back to Auto."""
    override = overrides.get(name)
    if override is not None and config.tier(override) is not None:
        return SeriesTier(override, True)
    return SeriesTier(auto_tier(tier_ids, config.tiers), False)


def earliest(dates: Iterable[date | None]) -> date | None:
    """The earliest date among these, or None when none is set."""
    present = [value for value in dates if value is not None]
    return min(present) if present else None


def _index(value: object) -> float:
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else 1.0


def _total(totals: Iterable[object | None]) -> int | None:
    positive = [int(value) for value in totals if isinstance(value, int) and not isinstance(value, bool) and value > 0]
    return max(positive) if positive else None


def _positions(owned: Mapping[int, float], end: int) -> list[tuple[float, int | None]]:
    filled = {index for index in owned.values() if index.is_integer()}
    gaps = [(float(number), None) for number in range(1, end + 1) if float(number) not in filled]
    placed = [(index, book) for book, index in owned.items()]
    return sorted((*gaps, *placed), key=_order)


def _end(owned: Mapping[int, float], total: int | None) -> int:
    if total is not None:
        return max(1, total)
    whole = [int(index) for index in owned.values() if index.is_integer()]
    return max(1, max(whole, default=0))


def _order(item: tuple[float, int | None]) -> tuple[bool, float, int]:
    index, book = item
    return (index != 1, index, -1 if book is None else book)


def _colour(ordered: list[tuple[float, int | None]], colours: Mapping[int, str]) -> str:
    for _, book in ordered:
        if book is not None and book in colours:
            return colours[book]
    return EMPTY_COLOUR


def display_number(index: float) -> str:
    return f'{index:g}'


def _lane_key(rank: Rank) -> tuple[bool, date, str, int]:
    date_read, text, order_id = rank
    return (date_read is None, date_read or date.min, text.casefold(), order_id)
