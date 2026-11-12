"""The values Page Defaults accepts, the tuples that list them, and the validators for its JSON shape."""

from collections.abc import Mapping
from typing import Any, Literal, cast

from .tiers import TierConfigError

Theme = Literal['system', 'light', 'dark']
PageWidth = Literal['narrow', 'normal', 'wide', 'full']
Gap = Literal['none', 'small', 'normal', 'large']
EmptyLane = Literal['default', 'hidden', 'custom']
CoverSize = Literal['small', 'normal', 'large']

THEMES: tuple[Theme, ...] = ('system', 'light', 'dark')
PAGE_WIDTHS: tuple[PageWidth, ...] = ('narrow', 'normal', 'wide', 'full')
GAPS: tuple[Gap, ...] = ('none', 'small', 'normal', 'large')
EMPTY_LANES: tuple[EmptyLane, ...] = ('default', 'hidden', 'custom')
COVER_SIZES: tuple[CoverSize, ...] = ('small', 'normal', 'large')


def require(name: str, value: str, allowed: tuple[str, ...]) -> None:
    """Raise ValueError when `value` is not one of `allowed`, naming the Page Defaults attribute."""
    if value not in allowed:
        raise ValueError(f'unknown {name}: {value!r}')


def choice[Choice: str](data: Mapping[str, Any], key: str, allowed: tuple[Choice, ...], default: Choice) -> Choice:
    """The stored choice for `key`, or `default` when absent; TierConfigError for a value outside `allowed`."""
    value = data.get(key, default)
    if value not in allowed:
        raise TierConfigError(f'unknown {key}: {value!r}')
    return cast(Choice, value)


def text(data: Mapping[str, Any], key: str, default: str) -> str:
    """The stored string for `key`, or `default` when absent; TierConfigError for a non-string."""
    value = data.get(key, default)
    if not isinstance(value, str):
        raise TierConfigError(f'{key} must be a string')
    return value


def flag(data: Mapping[str, Any], key: str, default: bool) -> bool:
    """The stored boolean for `key`, or `default` when absent; TierConfigError for a non-bool."""
    value = data.get(key, default)
    if not isinstance(value, bool):
        raise TierConfigError(f'{key} must be true or false')
    return value
