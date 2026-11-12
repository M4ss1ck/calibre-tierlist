"""Compile Series Stacks through the facade: placeholders, totals, and colour."""

from datetime import UTC, date, datetime
from typing import cast

from fakes import FakeCovers, FakeLibrary, FakePrefs

from tierlist.app import TIER_CONFIG_KEY, TierList
from tierlist.compile import CompileRequest, Series
from tierlist.tiers import Tier, TierConfig

NOW = datetime(2026, 11, 6, 12, 0, tzinfo=UTC)
TODAY = date(2026, 11, 6)
CONFIG = TierConfig(tiers=(Tier('s', 'S', '#ff7f7f'),))


def request(*book_ids: int) -> CompileRequest:
    return CompileRequest('library', book_ids, 'Lib', '0.1.0')


def compile_series(
    indexes: dict[int, float],
    config: TierConfig = CONFIG,
    covers: FakeCovers | None = None,
    totals: dict[int, int] | None = None,
) -> Series:
    library = FakeLibrary(types={'#date_read': 'datetime', '#series_total': 'int'})
    prefs = FakePrefs({TIER_CONFIG_KEY: config.to_dict()})
    library.values['series_index'] = cast(dict[int, object], indexes)
    library.values['#tier'] = {book_id: 's' for book_id in indexes}
    library.values['series'] = {book_id: 'Dune' for book_id in indexes}
    library.values['#series_total'] = cast(dict[int, object], totals or {})
    app = TierList(library, prefs, lambda: TODAY, lambda: NOW, covers=covers or FakeCovers())
    return app.compile(request(*indexes)).series['Dune']


def numbers(series: Series) -> list[str]:
    return [position.number for position in series.positions]


def test_a_series_total_fills_placeholders_up_to_it() -> None:
    config = TierConfig(tiers=CONFIG.tiers, series_total_column='#series_total')

    series = compile_series({2: 2.0}, config, totals={2: 7})

    assert numbers(series) == ['1', '2', '3', '4', '5', '6', '7']


def test_gaps_without_a_total_only_reach_the_highest_owned_whole_index() -> None:
    series = compile_series({1: 1.0, 3: 3.0})

    assert numbers(series) == ['1', '2', '3']


def test_a_fractional_index_is_a_position_but_never_a_placeholder() -> None:
    series = compile_series({1: 2.5})

    assert numbers(series) == ['1', '2.5']
    assert series.positions[1].book == 1


def test_a_missing_book_one_puts_a_placeholder_in_front() -> None:
    series = compile_series({1: 2.0, 2: 3.0})

    assert numbers(series)[0] == '1'
    assert series.positions[0].book is None


def test_a_long_series_keeps_every_position_for_the_series_panel() -> None:
    config = TierConfig(tiers=CONFIG.tiers, series_total_column='#series_total')

    series = compile_series({1: 1.0}, config, totals={1: 10})

    assert numbers(series) == [str(number) for number in range(1, 11)]
    assert [position.book for position in series.positions] == [1, *[None] * 9]


def test_colour_comes_from_the_first_owned_book_with_a_cover() -> None:
    covers = FakeCovers(with_cover={2, 3}, colours={2: '#112233', 3: '#445566'})

    series = compile_series({1: 1.0, 2: 2.0, 3: 3.0}, covers=covers)

    assert series.colour == '#112233'
