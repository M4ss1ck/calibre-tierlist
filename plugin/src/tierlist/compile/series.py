"""Series Stacks: the ordered positions one series occupies on the board."""

from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date

from ..tiers import Tier, TierConfig
from .covers import EMPTY_COLOUR


@dataclass(frozen=True)
class Position:
    """One position in a Stack: the number a reader sees, and the owned book id or None for a Placeholder."""

    number: str
    book: int | None


@dataclass(frozen=True)
class Series:
    """One series on the board: its Placeholder colour, positions shown, how many were cut, and whether it is an
    Override."""

    colour: str
    positions: tuple[Position, ...]
    more: int
    override: bool


@dataclass(frozen=True)
class SeriesTier:
    """The Tier a series is shown in, and whether that Tier comes from an Override."""

    tier_id: str | None
    override: bool


def build_series(
    indexes: Mapping[int, object | None],
    totals: Iterable[object | None],
    stack_depth: int,
    colours: Mapping[int, str],
    override: bool,
) -> Series:
    """Build the Stack for one series from each member's series index and colour, truncated to `stack_depth` behind."""
    owned = {book: _index(index) for book, index in indexes.items()}
    ordered = _positions(owned, _end(owned, _total(totals)))
    shown = ordered[: 1 + max(0, stack_depth)]
    return Series(
        _colour(ordered, colours),
        tuple(Position(display_number(index), book) for index, book in shown),
        len(ordered) - len(shown),
        override,
    )


def stacks_for(series: Mapping[str, tuple[str | None, date | None]], tier: str | None) -> tuple[str, ...]:
    """The series names whose Stack sits in this Lane, ordered by earliest date read, undated last, then name."""
    chosen = [(date_read, name) for name, (lane, date_read) in series.items() if lane == tier]
    return tuple(name for _, name in sorted(chosen, key=_stack_key))


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


def _stack_key(item: tuple[date | None, str]) -> tuple[bool, date, str]:
    date_read, name = item
    return (date_read is None, date_read or date.min, name.casefold())
