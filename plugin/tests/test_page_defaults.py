"""Page Defaults: the built-in choices, their JSON shape, and the compile carrying them."""

import pytest
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
    defaults = DEFAULT_PAGE_DEFAULTS

    assert (
        defaults.theme,
        defaults.title,
        defaults.unranked_label,
        defaults.show_unranked,
        defaults.show_counts,
        defaults.show_library,
    ) == ('system', 'Tier List', 'Unranked', True, True, True)


def test_to_dict_uses_the_contract_camel_case_keys() -> None:
    assert DEFAULT_PAGE_DEFAULTS.to_dict() == {
        'theme': 'system',
        'title': 'Tier List',
        'unrankedLabel': 'Unranked',
        'showUnranked': True,
        'showCounts': True,
        'showLibrary': True,
    }


def test_round_trip_through_dict() -> None:
    defaults = PageDefaults('dark', 'My shelf', 'Someday', False, False, False)

    assert PageDefaults.from_dict(defaults.to_dict()) == defaults


def test_from_dict_fills_missing_fields_with_defaults() -> None:
    assert PageDefaults.from_dict({}) == DEFAULT_PAGE_DEFAULTS
    assert PageDefaults.from_dict({'theme': 'light'}) == PageDefaults(theme='light')


def test_from_dict_ignores_unknown_keys() -> None:
    assert PageDefaults.from_dict({'theme': 'light', 'retired': 3}) == PageDefaults(theme='light')


@pytest.mark.parametrize('theme', ['neon', '', 'Light', None])
def test_an_invalid_theme_is_rejected(theme: object) -> None:
    with pytest.raises(ValueError):
        PageDefaults.from_dict({'theme': theme})


def test_a_blank_title_or_label_falls_back_to_its_default() -> None:
    defaults = PageDefaults(title='   ', unranked_label=' \t')

    assert (defaults.title, defaults.unranked_label) == ('Tier List', 'Unranked')


def test_a_title_is_trimmed() -> None:
    assert PageDefaults(title='  My shelf  ').title == 'My shelf'


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
