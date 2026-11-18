"""Integration test for emblem sync: our rule in both cover icon prefs, and our icons in calibre's folder.

Run with ``calibre-debug -e plugin/itest/emblems.py`` after installing the zip into a throwaway
``CALIBRE_CONFIG_DIRECTORY``. Prints ``EMBLEMS OK``; use ``expect``, as calibre runs Python with -OO.
"""

import os
import sys
import tempfile
from dataclasses import replace
from typing import Any

from calibre.ebooks.metadata.book.base import Metadata
from calibre.ebooks.metadata.book.formatter import SafeFormat
from calibre.gui2 import Application
from calibre.library import db as open_db
from calibre_plugins.tierlist.calibre_ui.adapters import config_admin, tier_list
from calibre_plugins.tierlist.calibre_ui.emblem_sync import RULE_PREFS, icons_dir, sync_emblems
from calibre_plugins.tierlist.emblems import icon_name, is_ours
from calibre_plugins.tierlist.tiers import DEFAULT_TIER_CONFIG, Tier, TierConfig

FOREIGN = (['icon', 'title', "program: 'a.png'"], ['emblem', 'tags', "program: 'b.png'"])
DEFAULT_ICONS = {icon_name(tier) for tier in DEFAULT_TIER_CONFIG.tiers}
DUPLICATE = ['emblem', '#tier', "program:\n# tierlist-emblem\n''"]


def expect(ok: bool, message: object) -> None:
    if not ok:
        raise SystemExit(f'EMBLEMS FAIL: {message}')


def files() -> set[str]:
    """Every file name in calibre's cover symbol folder."""
    return set(os.listdir(icons_dir())) if os.path.isdir(icons_dir()) else set()


def stamps() -> dict[str, int]:
    return {name: os.stat(os.path.join(icons_dir(), name)).st_mtime_ns for name in files()}


def tier(config: TierConfig, tier_id: str) -> Tier:
    return next(tier for tier in config.tiers if tier.id == tier_id)


def open_library(path: str) -> Any:
    """A fresh library with two columns, a foreign rule in each pref, and the column offers answered."""
    db = open_db(path)
    db.create_custom_column('tier', 'Tier', 'text', False)
    db.create_custom_column('date_read', 'Date read', 'datetime', False)
    db.close()
    db = open_db(path)
    app = tier_list(db)
    app.mark_tier_column_offered()
    app.mark_read_column_offered()
    for pref, foreign in zip(RULE_PREFS, FOREIGN, strict=True):
        db.prefs.set(pref, [list(foreign)])
    return db


def marked(db: Any, pref: str) -> list[str]:
    """Our one marked rule in an icon pref."""
    ours = [rule for rule in rules(db, pref) if is_ours(rule)]
    expect(len(ours) == 1, f'{pref} holds {len(ours)} marked rules')
    return ours[0]


def rules(db: Any, pref: str) -> list[list[str]]:
    """The rules calibre holds for one icon pref, as lists, the way its own JSON stores them."""
    stored: list[list[str]] = db.prefs.get(pref, []) or []
    return [list(rule) for rule in stored]


def with_emblems(db: Any, emblems: bool) -> TierConfig:
    """Store this library's Tier Config with emblems on or off, and return what was stored."""
    admin = config_admin(db)
    admin.save(replace(admin.tier_config(), emblems=emblems))
    return admin.tier_config()


def check_enable(db: Any) -> None:
    """Enabling appends one marked rule after each pref's foreign rule, and one icon file per Tier."""
    expect(sync_emblems(db, with_emblems(db, True)) is True, 'the enabling sync changed no pref')
    for pref, foreign in zip(RULE_PREFS, FOREIGN, strict=True):
        found = rules(db, pref)
        expect(len(found) == 2 and found[0] == foreign and is_ours(found[1]), f'{pref} holds {found}')
    expect(rules(db, RULE_PREFS[0])[1] == rules(db, RULE_PREFS[1])[1], 'the prefs hold different marked rules')
    expect(DEFAULT_ICONS <= files(), f'missing icons: {sorted(DEFAULT_ICONS - files())}')
    before, frozen = [rules(db, pref) for pref in RULE_PREFS], stamps()
    expect(sync_emblems(db, config_admin(db).tier_config()) is False, 'the second sync reported a change')
    expect([rules(db, pref) for pref in RULE_PREFS] == before and stamps() == frozen, 'the second sync wrote')
    ours = rules(db, RULE_PREFS[0])[1]
    db.prefs.set(RULE_PREFS[0], [ours, list(FOREIGN[0]), list(DUPLICATE)])
    sync_emblems(db, config_admin(db).tier_config())
    expect(rules(db, RULE_PREFS[0]) == [ours, list(FOREIGN[0])], f'{rules(db, RULE_PREFS[0])}')


def check_edits(db: Any) -> None:
    """Our template names the book's Tier icon, and a label change keeps it while adding the new icon."""
    book_id = db.new_api.create_book_entry(Metadata('Book', ['Author']))
    tier_list(db).set_book_tier([book_id], 'a')
    mi = db.new_api.get_metadata(book_id)
    config = config_admin(db).tier_config()
    template = marked(db, RULE_PREFS[0])[2]
    expect(SafeFormat().safe_format(template, mi, 'ERR', mi) == icon_name(tier(config, 'a')), 'the template')
    admin, old = config_admin(db), icon_name(tier(config, 'a'))
    places = [rules(db, pref).index(marked(db, pref)) for pref in RULE_PREFS]
    renamed = tuple(replace(t, label='Top') if t.id == 'a' else t for t in config.tiers)
    admin.save(replace(config, tiers=renamed))
    expect(sync_emblems(db, admin.tier_config()) is True, 'the rename sync kept the old icon name')
    added = icon_name(tier(admin.tier_config(), 'a'))
    for pref, place in zip(RULE_PREFS, places, strict=True):
        template = marked(db, pref)[2]
        expect(rules(db, pref).index(marked(db, pref)) == place, f'{pref}: the rename moved our rule')
        expect(added in template and old not in template, f'{pref}: the rename left {template!r}')
    expect(added in files() and old in files(), f'the renamed icon {added} was not written beside {old}')


def check_disable(db: Any) -> None:
    """Turning emblems off removes only our rules, and the icons stay."""
    expect(sync_emblems(db, with_emblems(db, False)) is True, 'the disabling sync changed no pref')
    for pref, foreign in zip(RULE_PREFS, FOREIGN, strict=True):
        expect(rules(db, pref) == [list(foreign)], f'{pref} after disabling holds {rules(db, pref)}')
    expect(DEFAULT_ICONS <= files(), 'disabling deleted icons')


def main() -> int:
    Application([])
    with tempfile.TemporaryDirectory() as tmp:
        db = open_library(tmp + '/emblems')
        try:
            check_enable(db)
            check_edits(db)
            check_disable(db)
        finally:
            db.close()
    print('EMBLEMS OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
