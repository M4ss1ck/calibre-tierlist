"""Arrange View staging: what dragging a Stack or Card means, before Settings writes anything."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Literal

from .compile import TierListData
from .compile.covers import EMPTY_COLOUR
from .lane_order import UNRANKED_LANE, Place
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
        return ('series', str(self.key)) if self.kind == 'series' else ('book', int(self.key))


class Arrange:
    """A staged board: Lanes of Stacks and Cards, with drops kept in memory until Settings saves."""

    def __init__(
        self, tiers: Sequence[Tier], lanes: Mapping[str, Sequence[ArrangeItem]], overrides: Mapping[str, str]
    ) -> None:
        self.tiers = tuple(tiers)
        self._lanes: dict[str, list[ArrangeItem]] = {key: list(items) for key, items in lanes.items()}
        for tier in self.tiers:
            self._lanes.setdefault(tier.id, [])
        self._lanes.setdefault(UNRANKED_LANE, [])
        self._overrides = dict(overrides)
        self._books: dict[int, str | None] = {}

    @classmethod
    def from_data(cls, data: TierListData, overrides: Mapping[str, str]) -> Arrange:
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
        return cls(data.tiers, lanes, overrides)

    def lanes(self) -> tuple[tuple[Tier | None, tuple[ArrangeItem, ...]], ...]:
        """Each Lane's Tier (None for the Unranked Lane) and its items, in board order."""
        tiers: list[Tier | None] = [*self.tiers, None]
        return tuple((tier, tuple(self._lanes[_key(None if tier is None else tier.id)])) for tier in tiers)

    def move(self, kind: Kind, key: str | int, target: str | None, index: int = -1) -> None:
        """Stage a drop: move a Stack or Card to `target` (None for Unranked) at `index`, appending when negative.

        A Stack dropped on another Tier's Lane takes that Override, or loses it on the Unranked Lane; a Card
        dropped on another Lane takes that Book Tier, or loses it on the Unranked Lane.
        """
        place = _place(kind, key)
        source, old = self._locate(place)
        target_key = _key(target)
        item = self._lanes[source].pop(old)
        if index < 0:
            index = len(self._lanes[target_key])
        elif source == target_key and old < index:
            index -= 1
        index = max(0, min(index, len(self._lanes[target_key])))
        if source != target_key:
            self._retier(kind, key, target)
        self._lanes[target_key].insert(index, item)

    def order(self) -> dict[str, list[Place]]:
        """Each Lane's places in the staged order, by Lane key."""
        return {key: [item.place for item in items] for key, items in self._lanes.items() if items}

    def overrides(self) -> dict[str, str]:
        """The staged Override map."""
        return dict(self._overrides)

    def book_tiers(self) -> dict[int, str | None]:
        """The Book Tier of every Card moved since the board was built; None means the Unranked Lane."""
        return dict(self._books)

    def _locate(self, place: Place) -> tuple[str, int]:
        for lane_key, items in self._lanes.items():
            for index, item in enumerate(items):
                if item.place == place:
                    return lane_key, index
        raise KeyError(place)

    def _retier(self, kind: Kind, key: str | int, target: str | None) -> None:
        if kind == 'series':
            if target is None:
                self._overrides.pop(str(key), None)
            else:
                self._overrides[str(key)] = target
        else:
            self._books[int(key)] = target


def _key(tier: str | None) -> str:
    return tier or UNRANKED_LANE


def _place(kind: Kind, key: str | int) -> Place:
    return ('series', str(key)) if kind == 'series' else ('book', int(key))
