"""Emblem sync: our rule in calibre's cover icon prefs, and the Tier icons those rules name."""

import os
from typing import Any

from calibre.utils.config import config_dir

from ..emblems import emblem_rule, icon_name, merge_rules
from ..tiers import TierConfig
from .adapters import config_admin
from .emblem_icon import emblem_png

RULE_PREFS = ('cover_grid_icon_rules', 'bookshelf_icon_rules')


def icons_dir() -> str:
    """calibre's global folder of cover symbols, which the rules of every library point into."""
    return os.path.join(config_dir, 'cc_icons')


def sync_emblems(db: Any, config: TierConfig) -> bool:
    """Put our rule in both icon rule prefs and write every missing Tier icon; True when a pref or icon changed."""
    ours = emblem_rule(config.tier_column, config.tiers) if config.emblems else None
    rules = 0
    for pref in RULE_PREFS:
        current: list[list[str]] = db.prefs.get(pref, []) or []
        merged = merge_rules(current, ours)
        if [tuple(rule) for rule in current] != merged:
            db.prefs.set(pref, [list(rule) for rule in merged])
            rules += 1
    icons = _write_icons(config) if config.emblems else 0
    print(f'tierlist: synced {rules} emblem rules, {icons} icons')
    return rules + icons > 0


def sync_library(gui: Any, db: Any) -> None:
    """Sync this library's emblems, then clear calibre's cover emblems so they show without a restart."""
    if not sync_emblems(db, config_admin(db).tier_config()):
        return
    model = gui.library_view.model()
    model.beginResetModel()
    model.endResetModel()


def _write_icons(config: TierConfig) -> int:
    """Write each Tier's icon that is missing; never delete one, as another library may name it."""
    os.makedirs(icons_dir(), exist_ok=True)
    written = 0
    for tier in config.tiers:
        path = os.path.join(icons_dir(), icon_name(tier))
        if not os.path.exists(path):
            with open(path, 'wb') as file:
                file.write(emblem_png(tier))
            written += 1
    return written
