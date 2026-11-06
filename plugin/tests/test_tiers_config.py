"""Tier Config: the default Tiers, and the JSON shape it round trips through."""

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


def test_round_trip_through_dict() -> None:
    config = TierConfig(
        tiers=(Tier('s', 'S', '#ff7f7f', 'The best'), Tier('a', 'A', '#ffbf7f')),
        tier_column='#rank',
    )
    assert TierConfig.from_dict(config.to_dict()) == config


def test_from_dict_fills_missing_description_and_tier_column() -> None:
    config = TierConfig.from_dict({'tiers': [{'id': 's', 'label': 'S', 'colour': '#ff7f7f'}]})
    assert config == TierConfig(tiers=(Tier('s', 'S', '#ff7f7f'),), tier_column='#tier')
    assert config.tiers[0].description == ''


def test_tier_returns_hit_and_miss() -> None:
    assert DEFAULT_TIER_CONFIG.tier('a') == Tier('a', 'A', '#ffbf7f')
    assert DEFAULT_TIER_CONFIG.tier('z') is None
