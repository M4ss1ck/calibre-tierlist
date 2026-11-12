"""The config-dialog facade: book counts, tier removal, saved-search sync, and orphans."""

from datetime import date

import pytest
from fakes import FakeLibrary, FakePrefs, FakeSavedSearches

from tierlist.app import TIER_CONFIG_KEY
from tierlist.config_admin import ConfigAdmin
from tierlist.series_tiers import SERIES_TIER_OVERRIDES_KEY
from tierlist.tiers import DEFAULT_TIER_CONFIG, Tier, TierConfig, TierConfigError, dump_config

SEARCHES = {'Tier S': '#tier:"=s"', 'Tier A': '#tier:"=a"'}


def config(*tiers: Tier, column: str = '#tier') -> TierConfig:
    return TierConfig(tiers=tiers, tier_column=column, read_column='#read')


CONFIG = config(Tier('s', 'S', '#ff7f7f'), Tier('a', 'A', '#ffbf7f'))
KEPT = config(Tier('s', 'S', '#ff7f7f'))
RENAMED = config(Tier('s', 'S+', '#123456'), Tier('a', 'A', '#ffbf7f'))
MOVED = config(*CONFIG.tiers, column='#rank')


def make(
    config_: TierConfig | None = CONFIG,
    columns: tuple[str, ...] = ('#tier',),
    types: dict[str, str] | None = None,
    searches: dict[str, str] | None = None,
) -> tuple[ConfigAdmin, FakeLibrary, FakePrefs, FakeSavedSearches]:
    library = FakeLibrary(columns, types)
    prefs = FakePrefs({} if config_ is None else {TIER_CONFIG_KEY: config_.to_dict()})
    saved = FakeSavedSearches(searches)
    return ConfigAdmin(library, prefs, saved), library, prefs, saved


def test_tier_config_falls_back_to_the_default() -> None:
    admin, _, _, _ = make(config_=None)
    assert admin.tier_config() == DEFAULT_TIER_CONFIG


def test_book_count_is_zero_without_the_tier_column_and_counts_otherwise() -> None:
    admin, library, _, _ = make()
    library.values['#tier'] = {1: 's', 2: 'a', 3: 's'}
    assert admin.book_count('s') == 2 and admin.book_count('b') == 0
    missing, library, _, _ = make(columns=())
    library.values['#tier'] = {1: 's'}
    assert missing.book_count('s') == 0


def test_rename_and_recolour_write_no_books() -> None:
    admin, library, _, _ = make()
    library.values['#tier'] = {1: 's', 2: 'a'}
    library.values['#read'] = {1: date(2024, 1, 1), 2: date(2024, 1, 2)}
    before = {name: dict(values) for name, values in library.values.items()}
    admin.save(RENAMED)
    assert library.values == before and library.writes == 0


def test_removing_a_tier_clears_only_its_books_and_keeps_read_state() -> None:
    admin, library, _, _ = make(types={'#read': 'datetime'})
    library.values['#tier'] = {1: 's', 2: 'a', 3: 'a'}
    library.values['#read'] = {1: date(2020, 1, 1), 2: date(2021, 1, 1), 3: date(2022, 1, 1)}
    admin.save(KEPT)
    assert library.values['#tier'] == {1: 's'}
    assert library.values['#read'] == {1: date(2020, 1, 1), 2: date(2021, 1, 1), 3: date(2022, 1, 1)}


def test_save_stores_a_valid_config_and_rejects_an_invalid_one() -> None:
    admin, _, prefs, _ = make()
    admin.save(KEPT)
    assert prefs.data[TIER_CONFIG_KEY] == KEPT.to_dict()
    with pytest.raises(TierConfigError):
        admin.save(TierConfig(tiers=()))
    assert prefs.data[TIER_CONFIG_KEY] == KEPT.to_dict()


def test_saving_creates_or_recreates_one_search_per_tier() -> None:
    admin, _, _, searches = make(config_=KEPT, searches={'Tier S': '#tier:"=s"'})
    admin.save(CONFIG)
    assert searches.searches == SEARCHES
    del searches.searches['Tier A']
    admin.save(CONFIG)
    assert searches.searches == SEARCHES


def test_renaming_a_tier_renames_its_search() -> None:
    admin, _, _, searches = make(searches=dict(SEARCHES))
    admin.save(RENAMED)
    assert searches.searches == {'Tier S+': '#tier:"=s"', 'Tier A': '#tier:"=a"'}


def test_swapping_two_labels_keeps_both_searches() -> None:
    swapped = config(Tier('s', 'A', '#ff7f7f'), Tier('a', 'S', '#ffbf7f'))
    admin, _, _, searches = make(searches=dict(SEARCHES))
    admin.save(swapped)
    assert searches.searches == {'Tier A': '#tier:"=s"', 'Tier S': '#tier:"=a"'}


def test_removing_a_tier_removes_its_search() -> None:
    admin, _, _, searches = make(searches=dict(SEARCHES))
    admin.save(KEPT)
    assert searches.searches == {'Tier S': '#tier:"=s"'}


def test_changing_the_tier_column_requeries_and_unrelated_searches_stay() -> None:
    admin, _, _, searches = make(searches={**SEARCHES, 'My books': 'tag:x'})
    admin.save(MOVED)
    assert searches.searches == {'Tier S': '#rank:"=s"', 'Tier A': '#rank:"=a"', 'My books': 'tag:x'}


def test_import_parses_without_saving_and_export_round_trips() -> None:
    admin, _, prefs, _ = make()
    before = dict(prefs.data)
    old = admin.parse_settings_export(dump_config(CONFIG))
    assert old.tier_config == CONFIG and old.page_defaults is None and prefs.data == before
    export = admin.parse_settings_export(admin.export_settings(CONFIG, admin.page_defaults(), include=False))
    assert export.tier_config == CONFIG and export.page_defaults == admin.page_defaults()


def test_import_rejects_bad_json_and_reports_a_missing_field() -> None:
    admin, _, _, _ = make()
    with pytest.raises(TierConfigError, match='Not valid JSON'):
        admin.parse_settings_export('{oops')
    with pytest.raises(TierConfigError, match='Missing field: tiers'):
        admin.parse_settings_export('{}')


def test_orphans_lists_overrides_with_no_series() -> None:
    admin, library, prefs, _ = make()
    library.values['series'] = {1: 'Dune'}
    prefs.data[SERIES_TIER_OVERRIDES_KEY] = {'Dune': 's', 'Old': 'a'}
    assert admin.orphans() == ['Old']


def test_reattach_moves_the_override_to_the_new_series() -> None:
    admin, library, prefs, _ = make()
    library.values['series'] = {1: 'Dune'}
    prefs.data[SERIES_TIER_OVERRIDES_KEY] = {'Old': 's'}
    admin.reattach_orphan('Old', 'Dune')
    assert prefs.data[SERIES_TIER_OVERRIDES_KEY] == {'Dune': 's'} and admin.orphans() == []


def test_delete_orphans_drops_them_and_keeps_live_overrides() -> None:
    admin, library, prefs, _ = make()
    library.values['series'] = {1: 'Dune'}
    prefs.data[SERIES_TIER_OVERRIDES_KEY] = {'Old': 's', 'Older': 'a', 'Dune': 'b'}
    admin.delete_orphans(['Old', 'Older'])
    assert prefs.data[SERIES_TIER_OVERRIDES_KEY] == {'Dune': 'b'}
