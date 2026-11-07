"""Compile Series Tiers from the Override map: an Override wins over Auto while its Tier still exists."""

from datetime import UTC, datetime

from fakes import FakeCovers, FakeLibrary

from tierlist.compile import Generated, TierListData
from tierlist.compile.build import build, compile_data
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


def unread_library() -> FakeLibrary:
    """Two unread, untiered Dune books."""
    library = FakeLibrary()
    library.values['title'] = {1: 'Dune', 2: 'Dune Messiah'}
    library.values['series'] = {1: 'Dune', 2: 'Dune'}
    library.values['series_index'] = {1: 1.0, 2: 2.0}
    return library


def compile_unread(overrides: dict[str, str]) -> TierListData:
    generated = Generated(NOW, 'Lib', 'library', '0.1.0')
    return compile_data(generated, unread_library(), FakeCovers(), 'webp', CONFIG, [1, 2], overrides)


def test_an_override_puts_an_unread_untiered_series_on_the_board() -> None:
    data = compile_unread({'Dune': 'a'})

    assert data.lanes[1].stacks == ('Dune',)
    assert data.series['Dune'].override is True


def test_an_override_to_a_deleted_tier_leaves_an_unread_untiered_series_off_the_board() -> None:
    data = compile_unread({'Dune': 'z'})

    assert data.series == {}
    assert all(lane.stacks == () for lane in data.lanes)
