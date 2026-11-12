"""Page Defaults: the built-in choices, their JSON shape, and the compile carrying them."""

from dataclasses import astuple

from fakes import FakeLibrary, FakePrefs

from tierlist.app import TIER_CONFIG_KEY, TierList
from tierlist.compile import CompileRequest
from tierlist.page_defaults import (
    DEFAULT_PAGE_DEFAULTS,
    PAGE_DEFAULTS_KEY,
    PageDefaults,
    load_defaults,
    save_defaults,
)
from tierlist.tiers import Tier, TierConfig

CONFIG = TierConfig(tiers=(Tier('s', 'S', '#ff7f7f'),))


def test_built_in_defaults_match_todays_page() -> None:
    assert astuple(DEFAULT_PAGE_DEFAULTS) == (
        'system',
        'Tier List',
        'Unranked',
        True,
        True,
        True,
        'normal',
        True,
        False,
        'none',
        'default',
        '',
        True,
        True,
        True,
        'normal',
        'normal',
    )


def test_to_dict_uses_the_contract_camel_case_keys() -> None:
    assert DEFAULT_PAGE_DEFAULTS.to_dict() == {
        'theme': 'system',
        'title': 'Tier List',
        'unrankedLabel': 'Unranked',
        'showUnranked': True,
        'showCounts': True,
        'showLibrary': True,
        'pageWidth': 'normal',
        'showLabels': True,
        'showDescriptions': False,
        'laneGap': 'none',
        'emptyLane': 'default',
        'emptyLaneText': '',
        'showCaptions': True,
        'showReadCount': True,
        'showSheets': True,
        'coverSize': 'normal',
        'coverGap': 'normal',
    }


def test_round_trip_through_dict() -> None:
    defaults = PageDefaults(
        theme='dark',
        title='My shelf',
        unranked_label='Someday',
        show_unranked=False,
        show_counts=False,
        show_library=False,
        page_width='full',
        show_labels=False,
        show_descriptions=True,
        lane_gap='large',
        empty_lane='custom',
        empty_lane_text='Nothing yet',
        show_captions=False,
        show_read_count=False,
        show_sheets=False,
        cover_size='large',
        cover_gap='none',
    )

    assert PageDefaults.from_dict(defaults.to_dict()) == defaults


def test_from_dict_fills_missing_fields_with_defaults() -> None:
    assert PageDefaults.from_dict({}) == DEFAULT_PAGE_DEFAULTS
    assert PageDefaults.from_dict({'theme': 'light'}) == PageDefaults(theme='light')


def test_from_dict_ignores_unknown_keys() -> None:
    assert PageDefaults.from_dict({'theme': 'light', 'retired': 3}) == PageDefaults(theme='light')


def test_defaults_stored_before_the_new_fields_load_with_their_defaults() -> None:
    old = {
        'theme': 'dark',
        'title': 'My shelf',
        'unrankedLabel': 'Someday',
        'showUnranked': False,
        'showCounts': False,
        'showLibrary': False,
    }

    assert PageDefaults.from_dict(old).to_dict() == {**DEFAULT_PAGE_DEFAULTS.to_dict(), **old}


def test_a_blank_title_or_label_falls_back_to_its_default() -> None:
    defaults = PageDefaults(title='   ', unranked_label=' \t')

    assert (defaults.title, defaults.unranked_label) == ('Tier List', 'Unranked')


def test_a_title_is_trimmed() -> None:
    assert PageDefaults(title='  My shelf  ').title == 'My shelf'


def test_an_empty_lane_message_is_trimmed_and_may_stay_blank() -> None:
    assert PageDefaults(empty_lane='custom', empty_lane_text='  Nothing  ').empty_lane_text == 'Nothing'
    assert PageDefaults(empty_lane='custom', empty_lane_text='   ').empty_lane_text == ''


def test_prefs_read_as_defaults_when_missing_and_save_round_trips() -> None:
    prefs = FakePrefs()

    assert load_defaults(prefs) == DEFAULT_PAGE_DEFAULTS
    save_defaults(prefs, PageDefaults(theme='dark'))
    assert prefs.data[PAGE_DEFAULTS_KEY] == PageDefaults(theme='dark').to_dict()
    assert load_defaults(prefs) == PageDefaults(theme='dark')


def test_compile_carries_the_stored_page_defaults() -> None:
    library = FakeLibrary(types={'#date_read': 'datetime'})
    library.values['#tier'] = {1: 's'}
    prefs = FakePrefs({TIER_CONFIG_KEY: CONFIG.to_dict(), PAGE_DEFAULTS_KEY: PageDefaults(theme='light').to_dict()})
    app = TierList(library, prefs)

    data = app.compile(CompileRequest('library', (1,), 'Lib', '0.1.0'))

    assert data.page_defaults == PageDefaults(theme='light')
    assert data.to_dict()['pageDefaults'] == PageDefaults(theme='light').to_dict()
