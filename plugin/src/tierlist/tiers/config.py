"""Tier Config: the ordered Tiers for one library and the columns holding Book Tier and Read State."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

DEFAULT_TIER_COLUMN = '#tier'
DEFAULT_READ_COLUMN = '#date_read'
MIN_STACK_DEPTH = 0
MAX_STACK_DEPTH = 6
DEFAULT_STACK_DEPTH = 3


@dataclass(frozen=True)
class Tier:
    """A rank in Tier Config: a stable id, the label a reader sees, a colour, and an optional description."""

    id: str
    label: str
    colour: str
    description: str = ''


@dataclass(frozen=True)
class TierConfig:
    """The ordered Tiers for one library, plus the lookup names of the column holding Book Tier and of the column
    holding Read State, how deep Stacks fan, and the optional numeric column holding each series' total."""

    tiers: tuple[Tier, ...]
    tier_column: str = DEFAULT_TIER_COLUMN
    read_column: str = DEFAULT_READ_COLUMN
    stack_depth: int = DEFAULT_STACK_DEPTH
    series_total_column: str = ''

    def tier(self, tier_id: str) -> Tier | None:
        """Return the Tier with this id, or None when Tier Config holds none."""
        return next((tier for tier in self.tiers if tier.id == tier_id), None)

    def to_dict(self) -> dict[str, Any]:
        """Serialise to the JSON shape Tier Config is stored and exported as."""
        return {
            'tiers': [
                {'id': tier.id, 'label': tier.label, 'colour': tier.colour, 'description': tier.description}
                for tier in self.tiers
            ],
            'tier_column': self.tier_column,
            'read_column': self.read_column,
            'stack_depth': self.stack_depth,
            'series_total_column': self.series_total_column,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> TierConfig:
        """Rebuild Tier Config from its JSON shape, the inverse of to_dict."""
        depth = int(data.get('stack_depth', DEFAULT_STACK_DEPTH))
        return cls(
            tiers=tuple(_tier_from_dict(raw) for raw in data['tiers']),
            tier_column=data.get('tier_column', DEFAULT_TIER_COLUMN),
            read_column=data.get('read_column', DEFAULT_READ_COLUMN),
            stack_depth=max(MIN_STACK_DEPTH, min(MAX_STACK_DEPTH, depth)),
            series_total_column=data.get('series_total_column', ''),
        )


def _tier_from_dict(raw: Mapping[str, Any]) -> Tier:
    return Tier(
        id=raw['id'],
        label=raw['label'],
        colour=raw['colour'],
        description=raw.get('description', ''),
    )


DEFAULT_TIER_CONFIG = TierConfig(
    tiers=(
        Tier('s', 'S', '#ff7f7f'),
        Tier('a', 'A', '#ffbf7f'),
        Tier('b', 'B', '#ffdf7f'),
        Tier('c', 'C', '#ffff7f'),
        Tier('d', 'D', '#bfff7f'),
        Tier('f', 'F', '#7fbfff'),
    ),
)
