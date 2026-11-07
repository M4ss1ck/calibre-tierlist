"""The Set series tier submenu: an Override per Tier, then Auto, beside Send to tier."""

from collections.abc import Callable, Iterable
from functools import partial
from typing import Any

from ..tiers import Tier

Register = Callable[[Any, str, str, str, Any], None]


def add_items(menu: Any, tiers: Iterable[Tier], action: Any, register: Register) -> None:
    """Fill the submenu from Tier Config; Overrides live in prefs, so no column has to exist."""
    for tier in tiers:
        register(
            menu,
            f'set-series-tier-{tier.id}',
            tier.label,
            _('Set series tier: {}').format(tier.label),
            partial(action.set_series_tier, tier.id),
        )
    menu.addSeparator()
    register(menu, 'set-series-tier-auto', _('Auto'), _('Set series tier: Auto'), action.clear_series_tier)
