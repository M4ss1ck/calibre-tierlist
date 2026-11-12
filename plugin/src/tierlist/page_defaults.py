"""Page Defaults: the choices a compiled page opens with, stored per library."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal, cast

from .ports import Prefs

PAGE_DEFAULTS_KEY = 'page_defaults'
Theme = Literal['system', 'light', 'dark']
THEMES: tuple[Theme, ...] = ('system', 'light', 'dark')


@dataclass(frozen=True)
class PageDefaults:
    """The choices a compiled page opens with: theme, Sheet title, Unranked Lane label and whether it is shown,
    and whether the header shows the counts and the library name."""

    theme: Theme = 'system'
    title: str = 'Tier List'
    unranked_label: str = 'Unranked'
    show_unranked: bool = True
    show_counts: bool = True
    show_library: bool = True

    def __post_init__(self) -> None:
        if self.theme not in THEMES:
            raise ValueError(f'unknown theme: {self.theme!r}')
        object.__setattr__(self, 'title', self.title.strip() or 'Tier List')
        object.__setattr__(self, 'unranked_label', self.unranked_label.strip() or 'Unranked')

    def to_dict(self) -> dict[str, Any]:
        """Serialise to the contract's camelCase JSON shape."""
        return {
            'theme': self.theme,
            'title': self.title,
            'unrankedLabel': self.unranked_label,
            'showUnranked': self.show_unranked,
            'showCounts': self.show_counts,
            'showLibrary': self.show_library,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> PageDefaults:
        """Rebuild Page Defaults from their JSON shape, filling missing keys with the built-in defaults and
        ignoring keys this version does not know."""
        return cls(
            theme=cast('Theme', data.get('theme', 'system')),
            title=cast(str, data.get('title', 'Tier List')),
            unranked_label=cast(str, data.get('unrankedLabel', 'Unranked')),
            show_unranked=bool(data.get('showUnranked', True)),
            show_counts=bool(data.get('showCounts', True)),
            show_library=bool(data.get('showLibrary', True)),
        )


DEFAULT_PAGE_DEFAULTS = PageDefaults()


def load_defaults(prefs: Prefs) -> PageDefaults:
    """The Page Defaults stored for this library, or the built-in ones when absent."""
    stored = prefs.get(PAGE_DEFAULTS_KEY)
    if stored is None:
        return DEFAULT_PAGE_DEFAULTS
    return PageDefaults.from_dict(cast('Mapping[str, Any]', stored))


def save_defaults(prefs: Prefs, defaults: PageDefaults) -> None:
    """Store Page Defaults for this library."""
    prefs.set(PAGE_DEFAULTS_KEY, defaults.to_dict())
