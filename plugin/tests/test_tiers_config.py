"""Tier Config: the default Tiers, and the JSON shape it round trips through."""

import pytest

from tierlist.tiers import DEFAULT_TIER_CONFIG, Tier, TierConfig

DEFAULT_IDS = ('s', 'a', 'b', 'c', 'd', 'f')
DEFAULT_LABELS = ('S', 'A', 'B', 'C', 'D', 'F')
DEFAULT_COLOURS = ('#ff7f7f', '#ffbf7f', '#ffdf7f', '#ffff7f', '#bfff7f', '#7fbfff')


def test_default_tiers_are_s_to_f_in_order() -> None:
    assert tuple(tier.id for tier in DEFAULT_TIER_CONFIG.tiers) == DEFAULT_IDS
    assert tuple(tier.label for tier in DEFAULT_TIER_CONFIG.tiers) == DEFAULT_LABELS
    assert tuple(tier.colour for tier in DEFAULT_TIER_CONFIG.tiers) == DEFAULT_COLOURS


def test_default_tier_column_is_hash_tier() -> None:
    assert DEFAULT_TIER_CONFIG.tier_column == '#tier'


def test_default_read_column_is_hash_date_read() -> None:
    assert DEFAULT_TIER_CONFIG.read_column == '#date_read'


def test_round_trip_through_dict() -> None:
    config = TierConfig(
        tiers=(Tier('s', 'S', '#ff7f7f', 'The best'), Tier('a', 'A', '#ffbf7f')),
        tier_column='#rank',
        read_column='#read',
        series_total_column='#total',
    )
    assert TierConfig.from_dict(config.to_dict()) == config


def test_to_dict_carries_the_series_total_column_and_no_stack_depth() -> None:
    assert DEFAULT_TIER_CONFIG.to_dict()['series_total_column'] == ''
    assert 'stack_depth' not in DEFAULT_TIER_CONFIG.to_dict()


def test_to_dict_carries_the_read_column() -> None:
    assert DEFAULT_TIER_CONFIG.to_dict()['read_column'] == '#date_read'


def test_from_dict_fills_missing_description_tier_and_read_columns() -> None:
    config = TierConfig.from_dict({'tiers': [{'id': 's', 'label': 'S', 'colour': '#ff7f7f'}]})
    assert config == TierConfig(tiers=(Tier('s', 'S', '#ff7f7f'),), tier_column='#tier', read_column='#date_read')
    assert config.tiers[0].description == ''


def test_from_dict_defaults_the_series_total_column() -> None:
    assert TierConfig.from_dict({'tiers': []}).series_total_column == ''


@pytest.mark.parametrize('depth', [3, 3.0, 99, -2, 'deep', None])
def test_from_dict_ignores_a_stack_depth_from_an_older_version(depth: object) -> None:
    older = {**DEFAULT_TIER_CONFIG.to_dict(), 'stack_depth': depth}
    assert TierConfig.from_dict(older) == DEFAULT_TIER_CONFIG


def test_tier_returns_hit_and_miss() -> None:
    assert DEFAULT_TIER_CONFIG.tier('a') == Tier('a', 'A', '#ffbf7f')
    assert DEFAULT_TIER_CONFIG.tier('z') is None
