"""Compile Series Stacks through the facade: position order."""

from datetime import UTC, date, datetime

from fakes import FakeCovers, FakeLibrary, FakePrefs

from tierlist.app import TIER_CONFIG_KEY, TierList
from tierlist.compile import CompileRequest
from tierlist.tiers import Tier, TierConfig

NOW = datetime(2026, 11, 6, 12, 0, tzinfo=UTC)
TODAY = date(2026, 11, 6)
CONFIG = TierConfig(tiers=(Tier('s', 'S', '#ff7f7f'),))


def test_an_index_zero_prequel_sits_behind_book_one() -> None:
    library = FakeLibrary(types={'#date_read': 'datetime'})
    prefs = FakePrefs({TIER_CONFIG_KEY: CONFIG.to_dict()})
    library.values['series'] = {1: 'Dune', 2: 'Dune'}
    library.values['series_index'] = {1: 0.0, 2: 1.0}
    library.values['#tier'] = {1: 's'}
    app = TierList(library, prefs, lambda: TODAY, lambda: NOW, covers=FakeCovers())

    data = app.compile(CompileRequest('library', (1, 2), 'Lib', '0.1.0'))

    assert [position.number for position in data.series['Dune'].positions] == ['1', '0']
