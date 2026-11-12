"""Page Defaults: the choices a compiled page opens with, stored per library."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal, cast

from .ports import Prefs
from .tiers import TierConfigError

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
        """Rebuild Page Defaults from their JSON shape, filling missing keys with the built-in defaults, ignoring
        keys this version does not know, and raising TierConfigError for a value that is not one it can show."""
        return cls(
            theme=_theme(data),
            title=_text(data, 'title', 'Tier List'),
            unranked_label=_text(data, 'unrankedLabel', 'Unranked'),
            show_unranked=_flag(data, 'showUnranked'),
            show_counts=_flag(data, 'showCounts'),
            show_library=_flag(data, 'showLibrary'),
        )


def _theme(data: Mapping[str, Any]) -> Theme:
    value = data.get('theme', 'system')
    if value not in THEMES:
        raise TierConfigError(f'unknown theme: {value!r}')
    return value


def _text(data: Mapping[str, Any], key: str, default: str) -> str:
    value = data.get(key, default)
    if not isinstance(value, str):
        raise TierConfigError(f'{key} must be a string')
    return value


def _flag(data: Mapping[str, Any], key: str) -> bool:
    value = data.get(key, True)
    if not isinstance(value, bool):
        raise TierConfigError(f'{key} must be true or false')
    return value


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
