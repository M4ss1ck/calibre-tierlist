"""Tier Config validation, and the JSON import/export the config dialog uses."""

import json
import re
from typing import Any, cast

from .config import MAX_STACK_DEPTH, MIN_STACK_DEPTH, Tier, TierConfig

HEX_COLOUR = re.compile(r'#[0-9a-fA-F]{6}')


class TierConfigError(ValueError):
    """A Tier Config that cannot be used, with a message a reader can act on."""


def validate(config: TierConfig) -> None:
    """Raise TierConfigError unless every Tier has a unique id, a label, and a hex colour, and the depth is in bounds."""
    if not config.tiers:
        raise TierConfigError('Tier Config needs at least one Tier')
    for tier in config.tiers:
        _validate_tier(tier)
    _validate_ids(config.tiers)
    if not MIN_STACK_DEPTH <= config.stack_depth <= MAX_STACK_DEPTH:
        raise TierConfigError(
            f'Stack depth must be between {MIN_STACK_DEPTH} and {MAX_STACK_DEPTH}, not {config.stack_depth}'
        )


def _validate_tier(tier: Tier) -> None:
    if not tier.id.strip():
        raise TierConfigError(f'Tier id must not be empty: {tier.id!r}')
    if not tier.label.strip():
        raise TierConfigError(f'Tier label must not be empty for Tier {tier.id!r}')
    if HEX_COLOUR.fullmatch(tier.colour) is None:
        raise TierConfigError(f'Tier colour must be #rrggbb hex for Tier {tier.id!r}: {tier.colour!r}')


def _validate_ids(tiers: tuple[Tier, ...]) -> None:
    seen: set[str] = set()
    for tier in tiers:
        if tier.id in seen:
            raise TierConfigError(f'Duplicate Tier id: {tier.id!r}')
        seen.add(tier.id)


def parse_config(text: str) -> TierConfig:
    """Parse and validate imported JSON, turning every failure into a TierConfigError with a human message."""
    try:
        data: Any = json.loads(text)
    except json.JSONDecodeError as exc:
        raise TierConfigError(f'Not valid JSON: {exc}') from exc
    if not isinstance(data, dict):
        raise TierConfigError('Tier Config must be a JSON object')
    try:
        config = TierConfig.from_dict(cast('dict[str, Any]', data))
    except KeyError as exc:
        raise TierConfigError(f'Missing field: {exc.args[0]}') from exc
    except (TypeError, ValueError) as exc:
        raise TierConfigError(f'Not a valid Tier Config: {exc}') from exc
    validate(config)
    return config


def dump_config(config: TierConfig) -> str:
    """Serialise Tier Config as the indented JSON the config dialog exports."""
    return json.dumps(config.to_dict(), indent=2)
