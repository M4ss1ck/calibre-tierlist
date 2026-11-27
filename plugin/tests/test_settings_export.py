"""Settings Export: one JSON file carrying Tier Config, Page Defaults, and optional Lane Order."""

import json

import pytest
from fakes import FakeLibrary, FakePrefs, FakeSavedSearches

from tierlist.app import TIER_CONFIG_KEY
from tierlist.config_admin import ConfigAdmin
from tierlist.lane_order import LANE_ORDER_KEY, UNRANKED_LANE, Place
from tierlist.page_defaults import PAGE_DEFAULTS_KEY, PageDefaults
from tierlist.settings_export import KIND, LEGACY_OVERRIDES_KEY, VERSION, SettingsExport, parse_export
from tierlist.tiers import Tier, TierConfig, TierConfigError, dump_config

CONFIG = TierConfig(tiers=(Tier('s', 'S', '#ff7f7f'), Tier('a', 'A', '#ffbf7f')))
DEFAULTS = PageDefaults(theme='light', title='My shelf')
OVERRIDES = {'Dune': 's', 'Earthsea': 'a'}
ORDER: dict[str, list[Place]] = {'s': [('series', 'Dune'), ('book', 7)], UNRANKED_LANE: [('book', 3)]}
PREF_ORDER = {'s': [{'series': 'Dune'}, {'book': 7}], UNRANKED_LANE: [{'book': 3}]}


def make(prefs: dict[str, object] | None = None) -> tuple[ConfigAdmin, FakeLibrary, FakePrefs]:
    library = FakeLibrary()
    store = FakePrefs({} if prefs is None else prefs)
    return ConfigAdmin(library, store, FakeSavedSearches()), library, store


def test_export_with_extras_round_trips() -> None:
    admin, _, _ = make({LEGACY_OVERRIDES_KEY: OVERRIDES, LANE_ORDER_KEY: PREF_ORDER})

    data = json.loads(admin.export_settings(CONFIG, DEFAULTS, include=True))

    assert data['kind'] == KIND and data['version'] == VERSION
    assert set(data) == {'kind', 'version', 'tier_config', 'page_defaults', 'lane_order'}
    assert data['tier_config'] == CONFIG.to_dict() and data['page_defaults'] == DEFAULTS.to_dict()
    assert admin.parse_settings_export(json.dumps(data)) == SettingsExport(CONFIG, DEFAULTS, ORDER)


def test_export_without_the_checkbox_leaves_out_lane_order() -> None:
    admin, _, _ = make({LEGACY_OVERRIDES_KEY: OVERRIDES, LANE_ORDER_KEY: PREF_ORDER})

    data = json.loads(admin.export_settings(CONFIG, DEFAULTS, include=False))
    export = admin.parse_settings_export(json.dumps(data))

    assert 'overrides' not in data and 'lane_order' not in data
    assert export == SettingsExport(CONFIG, DEFAULTS)


def test_stored_extras_are_the_lane_order_to_be_replaced() -> None:
    admin, _, _ = make({LEGACY_OVERRIDES_KEY: OVERRIDES, LANE_ORDER_KEY: PREF_ORDER})
    empty, _, _ = make()

    assert admin.stored_extras() == SettingsExport(lane_order=ORDER)
    assert empty.stored_extras() == SettingsExport(lane_order={})


def test_an_old_bare_tier_config_still_imports() -> None:
    assert parse_export(dump_config(CONFIG)) == SettingsExport(CONFIG)


def test_a_file_without_page_defaults_keeps_the_stored_ones() -> None:
    admin, _, prefs = make(
        {
            TIER_CONFIG_KEY: CONFIG.to_dict(),
            PAGE_DEFAULTS_KEY: DEFAULTS.to_dict(),
            LANE_ORDER_KEY: PREF_ORDER,
        }
    )
    export = parse_export(json.dumps({'kind': KIND, 'version': VERSION, 'tier_config': CONFIG.to_dict()}))

    admin.apply_import(export)

    assert export.page_defaults is None and export.lane_order is None
    assert prefs.data[PAGE_DEFAULTS_KEY] == DEFAULTS.to_dict()
    assert prefs.data[LANE_ORDER_KEY] == PREF_ORDER


def test_an_export_stored_before_the_new_page_fields_loads_their_defaults() -> None:
    old = {
        'theme': 'dark',
        'title': 'Old shelf',
        'unrankedLabel': 'Someday',
        'showUnranked': False,
        'showCounts': True,
        'showLibrary': False,
    }
    export = parse_export(
        json.dumps({'kind': KIND, 'version': VERSION, 'tier_config': CONFIG.to_dict(), 'page_defaults': old})
    )

    assert export.page_defaults is not None
    assert export.page_defaults.to_dict() == {**PageDefaults().to_dict(), **old}


@pytest.mark.parametrize(
    ('section', 'value', 'message'),
    [
        ('tier_config', {'tiers': []}, 'at least one'),
        ('page_defaults', {'theme': 'neon'}, 'page_defaults'),
        ('page_defaults', [], 'page_defaults'),
        ('lane_order', {'s': [{'nope': 1}]}, 'Lane Order'),
    ],
)
def test_malformed_sections_are_rejected_with_a_readable_message(section: str, value: object, message: str) -> None:
    data = {'kind': KIND, 'version': VERSION, 'tier_config': CONFIG.to_dict(), section: value}

    with pytest.raises(TierConfigError, match=message):
        parse_export(json.dumps(data))


def test_bad_json_and_an_unknown_kind_or_version_are_rejected() -> None:
    with pytest.raises(TierConfigError, match='Not valid JSON'):
        parse_export('{oops')
    with pytest.raises(TierConfigError, match='kind'):
        parse_export(json.dumps({'kind': 'other', 'version': VERSION}))
    with pytest.raises(TierConfigError, match='version'):
        parse_export(json.dumps({'kind': KIND, 'version': 99}))


def test_applying_an_export_replaces_lane_order_and_prunes_it() -> None:
    admin, library, prefs = make(
        {LANE_ORDER_KEY: {'s': [{'series': 'Gone'}]}, PAGE_DEFAULTS_KEY: PageDefaults(theme='dark').to_dict()}
    )
    library.values['series'] = {1: 'Dune'}

    admin.apply_import(SettingsExport(CONFIG, DEFAULTS, {'s': [('series', 'Dune'), ('series', 'Gone')]}))

    assert prefs.data[LANE_ORDER_KEY] == {'s': [{'series': 'Dune'}]}
    assert prefs.data[PAGE_DEFAULTS_KEY] == PageDefaults(theme='dark').to_dict()


def test_an_old_export_with_overrides_still_imports_and_skips_them() -> None:
    admin, _, prefs = make()
    old = {'kind': KIND, 'version': VERSION, 'tier_config': CONFIG.to_dict(), 'overrides': OVERRIDES}
    malformed = {**old, 'overrides': ['not', 'a', 'map']}

    export = admin.parse_settings_export(json.dumps(old))
    admin.apply_import(export)

    assert export == SettingsExport(CONFIG) == parse_export(json.dumps(malformed))
    assert LEGACY_OVERRIDES_KEY not in prefs.data
