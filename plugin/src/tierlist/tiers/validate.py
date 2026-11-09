"""Tier Config validation, and the JSON import/export the config dialog uses."""

import builtins
import json
import re
from typing import Any, cast

from .config import MAX_STACK_DEPTH, MIN_STACK_DEPTH, Tier, TierConfig

HEX_COLOUR = re.compile(r'#[0-9a-fA-F]{6}')


def _untranslated(text: str) -> str:
    return text


# calibre installs `_` as a builtin at runtime; pytest has none.
_ = getattr(builtins, '_', _untranslated)


class TierConfigError(ValueError):
    """A Tier Config that cannot be used, with a message a reader can act on."""


def validate(config: TierConfig) -> None:
    """Raise TierConfigError unless every Tier has a unique id, a label, and a hex colour, and the depth is in bounds."""
    if not config.tiers:
        raise TierConfigError(_('Tier Config needs at least one Tier'))
    for tier in config.tiers:
        _validate_tier(tier)
    _validate_ids(config.tiers)
    _validate_labels(config.tiers)
    if not MIN_STACK_DEPTH <= config.stack_depth <= MAX_STACK_DEPTH:
        raise TierConfigError(
            _('Stack depth must be between %d and %d, not %d') % (MIN_STACK_DEPTH, MAX_STACK_DEPTH, config.stack_depth)
        )


def _validate_tier(tier: Tier) -> None:
    if not tier.id.strip():
        raise TierConfigError(_('Tier id must not be empty: %r') % tier.id)
    if not tier.label.strip():
        raise TierConfigError(_('Tier label must not be empty for Tier %r') % tier.id)
    if HEX_COLOUR.fullmatch(tier.colour) is None:
        raise TierConfigError(_('Tier colour must be #rrggbb hex for Tier %r: %r') % (tier.id, tier.colour))


def _validate_ids(tiers: tuple[Tier, ...]) -> None:
    seen: set[str] = set()
    for tier in tiers:
        if tier.id in seen:
            raise TierConfigError(_('Duplicate Tier id: %r') % tier.id)
        seen.add(tier.id)


def _validate_labels(tiers: tuple[Tier, ...]) -> None:
    seen: set[str] = set()
    for tier in tiers:
        label = tier.label.strip().lower()
        if label in seen:
            raise TierConfigError(_('Duplicate Tier label: %r') % tier.label)
        seen.add(label)


def parse_config(text: str) -> TierConfig:
    """Parse and validate imported JSON, turning every failure into a TierConfigError with a human message."""
    try:
        data: Any = json.loads(text)
    except json.JSONDecodeError as exc:
        raise TierConfigError(_('Not valid JSON: %s') % exc) from exc
    if not isinstance(data, dict):
        raise TierConfigError(_('Tier Config must be a JSON object'))
    try:
        config = TierConfig.from_dict(cast('dict[str, Any]', data))
    except KeyError as exc:
        raise TierConfigError(_('Missing field: %s') % exc.args[0]) from exc
    except (TypeError, ValueError) as exc:
        raise TierConfigError(_('Not a valid Tier Config: %s') % exc) from exc
    validate(config)
    return config


def dump_config(config: TierConfig) -> str:
    """Serialise Tier Config as the indented JSON the config dialog exports."""
    return json.dumps(config.to_dict(), indent=2)
