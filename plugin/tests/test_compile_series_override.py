"""Compile Series Tiers from the Override map: an Override wins over Auto while its Tier still exists."""

from datetime import UTC, datetime

from tierlist.compile import Generated, TierListData
from tierlist.compile.build import build
from tierlist.compile.rows import Row
from tierlist.tiers import Tier, TierConfig

NOW = datetime(2026, 11, 6, 12, 0, tzinfo=UTC)
CONFIG = TierConfig(tiers=(Tier('s', 'S', '#ff7f7f'), Tier('a', 'A', '#ffbf7f'), Tier('b', 'B', '#ffdf7f')))


def dune(*tiers: str | None) -> list[Row]:
    """One Dune book per Book Tier, each in its own series position."""
    return [Row(index, f'Dune {index}', tier, None, 'Dune', float(index)) for index, tier in enumerate(tiers, 1)]


def compile_with(rows: list[Row], overrides: dict[str, str]) -> TierListData:
    return build(Generated(NOW, 'Lib', 'library', '0.1.0'), CONFIG, rows, False, {}, overrides)


def test_an_override_wins_over_auto() -> None:
    data = compile_with(dune('s', 'a'), {'Dune': 'b'})

    assert data.lanes[2].stacks == ('Dune',)
    assert data.series['Dune'].override is True
    assert data.to_dict()['series']['Dune']['override'] is True


def test_a_series_without_an_override_stays_auto() -> None:
    data = compile_with(dune('s', 'a'), {})

    assert data.lanes[1].stacks == ('Dune',)
    assert data.series['Dune'].override is False


def test_an_override_to_a_deleted_tier_falls_back_to_auto() -> None:
    data = compile_with(dune('s'), {'Dune': 'z'})

    assert data.lanes[0].stacks == ('Dune',)
    assert data.series['Dune'].override is False


def test_an_override_for_a_series_not_on_the_board_is_ignored() -> None:
    data = compile_with(dune('s'), {'Earthsea': 'b'})

    assert 'Earthsea' not in data.series
    assert data.lanes[0].stacks == ('Dune',)
    assert data.series['Dune'].override is False
