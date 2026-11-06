"""Read State through the facade: marking read and unread over the fake ports."""

from datetime import date

import pytest
from fakes import FakeLibrary, FakePrefs

from tierlist.app import READ_COLUMN_OFFERED_KEY, TIER_CONFIG_KEY, TierList
from tierlist.tiers import DEFAULT_TIER_CONFIG, Tier, TierConfig

TODAY = date(2026, 11, 6)
OLD_DATE = date(2020, 1, 1)
READ_COLUMN = '#date_read'
DATATYPES = ('datetime', 'bool')
CUSTOM = TierConfig(tiers=(Tier('s', 'S-Tier', '#ff7f7f'), Tier('a', 'A-Tier', '#ffbf7f')), read_column='#elsewhere')


def facade(datatype: str | None, config: TierConfig | None = None) -> tuple[TierList, FakeLibrary, FakePrefs]:
    library = FakeLibrary(types={} if datatype is None else {READ_COLUMN: datatype})
    prefs = FakePrefs({} if config is None else {TIER_CONFIG_KEY: config.to_dict()})
    return TierList(library, prefs, lambda: TODAY), library, prefs


def read_value(datatype: str) -> object:
    return TODAY if datatype == 'datetime' else True


def stored_value(datatype: str) -> object:
    return OLD_DATE if datatype == 'datetime' else True


@pytest.mark.parametrize('datatype', DATATYPES)
def test_set_book_tier_marks_every_book_read(datatype: str) -> None:
    app, library, _ = facade(datatype)
    app.set_book_tier([1, 2], 's')
    assert library.values[READ_COLUMN] == {1: read_value(datatype), 2: read_value(datatype)}


@pytest.mark.parametrize('datatype', DATATYPES)
def test_existing_read_state_is_preserved_by_set_book_tier_and_mark_read(datatype: str) -> None:
    app, library, _ = facade(datatype)
    library.values[READ_COLUMN] = {1: stored_value(datatype)}
    app.set_book_tier([1], 'a')
    app.mark_read([1])
    assert library.values[READ_COLUMN] == {1: stored_value(datatype)}
    assert library.writes == 1


@pytest.mark.parametrize('datatype', DATATYPES)
def test_mark_read_fills_only_the_ids_still_empty(datatype: str) -> None:
    app, library, _ = facade(datatype)
    library.values[READ_COLUMN] = {1: stored_value(datatype)}
    app.mark_read([1, 2])
    assert library.values[READ_COLUMN] == {1: stored_value(datatype), 2: read_value(datatype)}
    assert library.writes == 1


@pytest.mark.parametrize('datatype', DATATYPES)
def test_mark_unread_clears_read_state_and_book_tier(datatype: str) -> None:
    app, library, _ = facade(datatype)
    app.set_book_tier([1, 2], 's')
    app.mark_unread([1])
    assert library.values[READ_COLUMN] == {2: read_value(datatype)}
    assert library.values['#tier'] == {2: 's'}
    assert library.writes == 4


@pytest.mark.parametrize('datatype', DATATYPES)
def test_clear_book_tier_keeps_read_state(datatype: str) -> None:
    app, library, _ = facade(datatype)
    app.set_book_tier([1], 's')
    app.clear_book_tier([1])
    assert library.values['#tier'] == {}
    assert library.values[READ_COLUMN] == {1: read_value(datatype)}


@pytest.mark.parametrize('datatype', DATATYPES)
def test_empty_selection_writes_nothing(datatype: str) -> None:
    app, library, _ = facade(datatype)
    app.mark_read([])
    app.mark_unread([])
    assert library.writes == 0


def test_mark_read_with_no_read_column_writes_nothing() -> None:
    app, library, _ = facade(None)
    app.mark_read([1, 2])
    assert library.writes == 0
    app.set_book_tier([1], 's')
    assert library.values['#tier'] == {1: 's'}
    assert library.writes == 1


def test_mark_read_with_an_unmapped_read_column_writes_nothing() -> None:
    config = TierConfig(tiers=DEFAULT_TIER_CONFIG.tiers, read_column='#missing')
    app, library, _ = facade('datetime', config)
    app.mark_read([1])
    assert library.writes == 0
    app.set_book_tier([1], 's')
    assert library.values['#tier'] == {1: 's'}


def test_read_column_candidates_are_only_datetime_and_bool_columns_sorted() -> None:
    library = FakeLibrary(columns=('#tier', '#notes'), types={'#read': 'bool', '#done': 'datetime', '#pages': 'int'})
    app = TierList(library, FakePrefs())
    assert app.read_column_candidates() == ['#done', '#read']


def test_map_read_column_stores_it_and_readiness_follows() -> None:
    prefs = FakePrefs()
    app = TierList(FakeLibrary(types={'#read': 'datetime'}), prefs)
    assert not app.read_column_ready()
    app.map_read_column('#read')
    assert app.read_column_ready()
    assert prefs.data[TIER_CONFIG_KEY] == TierConfig(tiers=DEFAULT_TIER_CONFIG.tiers, read_column='#read').to_dict()


def test_map_read_column_keeps_the_stored_tiers() -> None:
    app, _, prefs = facade('datetime', CUSTOM)
    app.map_read_column(READ_COLUMN)
    assert prefs.data[TIER_CONFIG_KEY] == TierConfig(tiers=CUSTOM.tiers, read_column=READ_COLUMN).to_dict()


def test_map_read_column_rejects_a_text_column() -> None:
    app, _, prefs = facade('datetime')
    with pytest.raises(ValueError):
        app.map_read_column('#tier')
    assert TIER_CONFIG_KEY not in prefs.data


def test_read_column_offer_defaults_to_not_offered() -> None:
    app, _, _ = facade('datetime')
    assert not app.read_column_offered()


def test_mark_read_column_offered_records_the_offer() -> None:
    app, _, prefs = facade('datetime')
    app.mark_read_column_offered()
    assert app.read_column_offered()
    assert prefs.data[READ_COLUMN_OFFERED_KEY] is True
