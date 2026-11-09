"""Integration test for the config-dialog adapter: saved searches follow their Tiers.

Run with ``calibre-debug -e plugin/itest/config_admin.py`` after installing
``dist/tierlist.zip`` with ``calibre-customize -a`` into a throwaway
``CALIBRE_CONFIG_DIRECTORY``. Prints ``CONFIG ADMIN OK`` and exits 0 on success.

calibre runs Python with -OO, which strips ``assert``; use ``expect``.
"""

import sys
import tempfile
from dataclasses import replace
from datetime import datetime
from typing import Any

from calibre.ebooks.metadata.book.base import Metadata
from calibre.gui2 import Application
from calibre.library import db as open_db
from calibre.utils.date import local_tz
from calibre_plugins.tierlist.calibre_ui.adapters import config_admin

USER_SEARCH = 'My books'
USER_QUERY = 'tag:mine'


def expect(ok: bool, message: object) -> None:
    if not ok:
        raise SystemExit(f'CONFIG ADMIN FAIL: {message}')


def open_library(path: str) -> Any:
    db = open_db(path)
    db.create_custom_column('tier', 'Tier', 'text', False)
    db.create_custom_column('date_read', 'Date read', 'datetime', False)
    db.close()
    return open_db(path)


def searches(db: Any) -> dict[str, str | None]:
    return {name: db.new_api.saved_search_lookup(name) for name in db.new_api.saved_search_names()}


def tier_searches(config: Any) -> dict[str, str]:
    """The saved search each Tier should own, by name."""
    return {f'Tier {tier.label}': f'{config.tier_column}:"={tier.id}"' for tier in config.tiers}


def check_sync(path: str) -> None:
    db = open_library(path)
    try:
        ids = [db.new_api.create_book_entry(Metadata(f'Book {n}', ['Author'])) for n in (1, 2)]
        read = datetime(2020, 5, 4, 12, tzinfo=local_tz)
        db.new_api.set_field('#tier', {ids[0]: 's', ids[1]: 'f'})
        db.new_api.set_field('#date_read', {ids[1]: read})
        db.new_api.saved_search_add(USER_SEARCH, USER_QUERY)
        admin = config_admin(db)

        config = admin.tier_config()
        admin.save(config)
        found = searches(db)
        expect(found == {**tier_searches(config), USER_SEARCH: USER_QUERY}, f'default save created {found}')
        expect(len(config.tiers) == 6, f'default Tier Config has {len(config.tiers)} Tiers')

        renamed = replace(config, tiers=tuple(replace(t, label='Top') if t.id == 's' else t for t in config.tiers))
        admin.save(renamed)
        found = searches(db)
        expect(found == {**tier_searches(renamed), USER_SEARCH: USER_QUERY}, f'rename left {found}')
        expect('Tier S' not in found and 'Tier Top' in found, f'rename left {sorted(found)}')
        expect(db.new_api.field_for('#tier', ids[0]) == 's', 'renaming a Tier changed its book')

        trimmed = replace(renamed, tiers=tuple(t for t in renamed.tiers if t.id != 'f'))
        admin.save(trimmed)
        found = searches(db)
        expect(found == {**tier_searches(trimmed), USER_SEARCH: USER_QUERY}, f'removal left {found}')
        expect('Tier F' not in found, f'removal left {sorted(found)}')
        expect(db.new_api.field_for('#tier', ids[1]) is None, 'removing a Tier kept its book')
        kept = db.new_api.field_for('#date_read', ids[1])
        expect(kept is not None and kept.astimezone(local_tz).date() == read.date(), f'read date changed: {kept}')
        expect(db.new_api.field_for('#tier', ids[0]) == 's', 'removing a Tier changed another Tier book')
    finally:
        db.close()


def main() -> int:
    Application([])
    with tempfile.TemporaryDirectory() as tmp:
        check_sync(tmp + '/searches')
    print('CONFIG ADMIN OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
