"""Page Defaults: every enum, flag and text field rejects a stored value the page could not show."""

from typing import Any, cast

import pytest
from fakes import FakePrefs

from tierlist.page_defaults import DEFAULT_PAGE_DEFAULTS, PAGE_DEFAULTS_KEY, PageDefaults, load_defaults
from tierlist.tiers import TierConfigError

ENUMS = ('theme', 'pageWidth', 'laneGap', 'emptyLane', 'coverSize', 'coverGap')
ENUM_ATTRS = ('theme', 'page_width', 'lane_gap', 'empty_lane', 'cover_size', 'cover_gap')
FLAGS = (
    'showUnranked',
    'showCounts',
    'showLibrary',
    'showLabels',
    'showDescriptions',
    'showCaptions',
    'showReadCount',
)
TEXTS = ('title', 'unrankedLabel', 'emptyLaneText')


@pytest.mark.parametrize('key', ENUMS)
@pytest.mark.parametrize('value', ['neon', '', None, 3])
def test_an_unknown_enum_value_is_rejected(key: str, value: object) -> None:
    with pytest.raises(TierConfigError, match=key):
        PageDefaults.from_dict({key: value})


@pytest.mark.parametrize('key', FLAGS)
def test_a_non_bool_flag_is_rejected(key: str) -> None:
    with pytest.raises(TierConfigError, match=key):
        PageDefaults.from_dict({key: 'false'})


@pytest.mark.parametrize('key', TEXTS)
def test_a_non_string_text_is_rejected(key: str) -> None:
    with pytest.raises(TierConfigError, match=key):
        PageDefaults.from_dict({key: 5})


@pytest.mark.parametrize('attr', ENUM_ATTRS)
def test_a_bad_enum_value_on_a_page_defaults_object_is_a_value_error(attr: str) -> None:
    with pytest.raises(ValueError, match=attr):
        PageDefaults(**cast(Any, {attr: 'neon'}))


def test_corrupt_stored_defaults_read_as_the_built_in_ones() -> None:
    assert load_defaults(FakePrefs({PAGE_DEFAULTS_KEY: {'theme': 'neon'}})) == DEFAULT_PAGE_DEFAULTS
    assert load_defaults(FakePrefs({PAGE_DEFAULTS_KEY: {'coverSize': 'huge'}})) == DEFAULT_PAGE_DEFAULTS
    assert load_defaults(FakePrefs({PAGE_DEFAULTS_KEY: ['not', 'a', 'mapping']})) == DEFAULT_PAGE_DEFAULTS
