"""Page Defaults: the choices a compiled page opens with, stored per library."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, cast

from .page_choices import (
    COVER_SIZES,
    EMPTY_LANES,
    GAPS,
    PAGE_WIDTHS,
    THEMES,
    CoverSize,
    EmptyLane,
    Gap,
    PageWidth,
    Theme,
    choice,
    flag,
    require,
    text,
)
from .ports import Prefs
from .tiers import TierConfigError

PAGE_DEFAULTS_KEY = 'page_defaults'


@dataclass(frozen=True)
class PageDefaults:
    """The choices a compiled page opens with: theme, Sheet title and Page Width; the header's counts and library
    name; the Lanes' labels, Tier descriptions, Lane Gap, Unranked Lane and Empty Lane Message; and the covers'
    Captions, Read Count, Cover Size and Cover Gap."""

    theme: Theme = 'system'
    title: str = 'Tier List'
    unranked_label: str = 'Unranked'
    show_unranked: bool = True
    show_counts: bool = True
    show_library: bool = True
    page_width: PageWidth = 'normal'
    show_labels: bool = True
    show_descriptions: bool = False
    lane_gap: Gap = 'none'
    empty_lane: EmptyLane = 'default'
    empty_lane_text: str = ''
    show_captions: bool = True
    show_read_count: bool = True
    cover_size: CoverSize = 'normal'
    cover_gap: Gap = 'normal'

    def __post_init__(self) -> None:
        require('theme', self.theme, THEMES)
        require('page_width', self.page_width, PAGE_WIDTHS)
        require('lane_gap', self.lane_gap, GAPS)
        require('empty_lane', self.empty_lane, EMPTY_LANES)
        require('cover_size', self.cover_size, COVER_SIZES)
        require('cover_gap', self.cover_gap, GAPS)
        object.__setattr__(self, 'title', self.title.strip() or 'Tier List')
        object.__setattr__(self, 'unranked_label', self.unranked_label.strip() or 'Unranked')
        object.__setattr__(self, 'empty_lane_text', self.empty_lane_text.strip())

    def to_dict(self) -> dict[str, Any]:
        """Serialise to the contract's camelCase JSON shape, in its key order."""
        return {
            'theme': self.theme,
            'title': self.title,
            'unrankedLabel': self.unranked_label,
            'showUnranked': self.show_unranked,
            'showCounts': self.show_counts,
            'showLibrary': self.show_library,
            'pageWidth': self.page_width,
            'showLabels': self.show_labels,
            'showDescriptions': self.show_descriptions,
            'laneGap': self.lane_gap,
            'emptyLane': self.empty_lane,
            'emptyLaneText': self.empty_lane_text,
            'showCaptions': self.show_captions,
            'showReadCount': self.show_read_count,
            'coverSize': self.cover_size,
            'coverGap': self.cover_gap,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> PageDefaults:
        """Rebuild Page Defaults from their JSON shape, filling missing keys with the built-in defaults, ignoring
        keys this version does not know, and raising TierConfigError for a value that is not one it can show."""
        return cls(
            theme=choice(data, 'theme', THEMES, 'system'),
            title=text(data, 'title', 'Tier List'),
            unranked_label=text(data, 'unrankedLabel', 'Unranked'),
            show_unranked=flag(data, 'showUnranked', True),
            show_counts=flag(data, 'showCounts', True),
            show_library=flag(data, 'showLibrary', True),
            page_width=choice(data, 'pageWidth', PAGE_WIDTHS, 'normal'),
            show_labels=flag(data, 'showLabels', True),
            show_descriptions=flag(data, 'showDescriptions', False),
            lane_gap=choice(data, 'laneGap', GAPS, 'none'),
            empty_lane=choice(data, 'emptyLane', EMPTY_LANES, 'default'),
            empty_lane_text=text(data, 'emptyLaneText', ''),
            show_captions=flag(data, 'showCaptions', True),
            show_read_count=flag(data, 'showReadCount', True),
            cover_size=choice(data, 'coverSize', COVER_SIZES, 'normal'),
            cover_gap=choice(data, 'coverGap', GAPS, 'normal'),
        )


DEFAULT_PAGE_DEFAULTS = PageDefaults()


def load_defaults(prefs: Prefs) -> PageDefaults:
    """The Page Defaults stored for this library, or the built-in ones when absent or too corrupt to read."""
    stored = prefs.get(PAGE_DEFAULTS_KEY)
    if not isinstance(stored, Mapping):
        return DEFAULT_PAGE_DEFAULTS
    try:
        return PageDefaults.from_dict(cast('Mapping[str, Any]', stored))
    except TierConfigError:
        return DEFAULT_PAGE_DEFAULTS


def save_defaults(prefs: Prefs, defaults: PageDefaults) -> None:
    """Store Page Defaults for this library."""
    prefs.set(PAGE_DEFAULTS_KEY, defaults.to_dict())
