"""Arrange View staging: what dragging a Stack or Card means, before Settings writes anything."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Literal

from .compile import TierListData
from .compile.covers import EMPTY_COLOUR
from .lane_order import UNRANKED_LANE, Place, place_for
from .tiers import Tier

Kind = Literal['series', 'book']
THUMB_WIDTH = 96


@dataclass(frozen=True)
class ArrangeItem:
    """One thing the Arrange View draws: a Stack by series name, or a Card by book id."""

    kind: Kind
    key: str | int
    label: str
    books: tuple[int, ...] = ()
    colour: str = EMPTY_COLOUR

    @property
    def place(self) -> Place:
        return place_for(self.kind, self.key)


class Arrange:
    """A staged board: Lanes of Stacks and Cards, with drops kept in memory until Settings saves."""

    def __init__(self, tiers: Sequence[Tier], lanes: Mapping[str, Sequence[ArrangeItem]]) -> None:
        self.tiers = tuple(tiers)
        self._lanes: dict[str, list[ArrangeItem]] = {key: list(items) for key, items in lanes.items()}
        for tier in self.tiers:
            self._lanes.setdefault(tier.id, [])
        self._lanes.setdefault(UNRANKED_LANE, [])

    @classmethod
    def from_data(cls, data: TierListData) -> Arrange:
        """The whole-library board the Arrange View shows, from compiled Tier List Data."""
        books = {book.id: book for book in data.books}
        lanes: dict[str, list[ArrangeItem]] = {}
        for lane in data.lanes:
            items: list[ArrangeItem] = []
            for entry in lane.items:
                if entry.stack is not None:
                    series = data.series[entry.stack]
                    owned = tuple(position.book for position in series.positions if position.book is not None)
                    items.append(ArrangeItem('series', entry.stack, entry.stack, owned, series.colour))
                elif entry.card is not None:
                    book = books[entry.card]
                    items.append(ArrangeItem('book', entry.card, book.title, (entry.card,)))
            lanes[lane.tier or UNRANKED_LANE] = items
        return cls(data.tiers, lanes)

    def lanes(self) -> tuple[tuple[Tier | None, tuple[ArrangeItem, ...]], ...]:
        """Each Lane's Tier (None for the Unranked Lane) and its items, in board order."""
        tiers: list[Tier | None] = [*self.tiers, None]
        return tuple((tier, tuple(self._lanes[_key(None if tier is None else tier.id)])) for tier in tiers)

    def move(self, kind: Kind, key: str | int, target: str | None, index: int = -1) -> bool:
        """Stage a drop of a Stack or Card on `target`'s Lane (None for Unranked) at `index`, appending when negative.

        Only a drop on its own Lane reorders it; a drop on another Lane is refused and changes nothing, since a
        Tier changes only through Book Tiers (ADR 0011). Returns whether the drop was taken.
        """
        source, old = self._locate(place_for(kind, key))
        lane = self._lanes[source]
        if source != _key(target):
            return False
        item = lane.pop(old)
        if index < 0:
            index = len(lane)
        elif old < index:
            index -= 1
        lane.insert(max(0, min(index, len(lane))), item)
        return True

    def order(self) -> dict[str, list[Place]]:
        """Each Lane's places in the staged order, by Lane key."""
        return {key: [item.place for item in items] for key, items in self._lanes.items() if items}

    def _locate(self, place: Place) -> tuple[str, int]:
        for lane_key, items in self._lanes.items():
            for index, item in enumerate(items):
                if item.place == place:
                    return lane_key, index
        raise KeyError(place)


def _key(tier: str | None) -> str:
    return tier or UNRANKED_LANE
