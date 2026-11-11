"""The compiled payload validates against the JSON Schema and matches the checked-in fixture."""

import json
import os
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, Protocol, cast

from fakes import FakeCovers, FakeLibrary, FakePrefs
from jsonschema import Draft202012Validator, FormatChecker

from tierlist.app import TIER_CONFIG_KEY, TierList
from tierlist.compile import CompileRequest
from tierlist.series_tiers import SERIES_TIER_OVERRIDES_KEY
from tierlist.tiers import Tier, TierConfig

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / 'contract' / 'tierlist.schema.json'
FIXTURE_PATH = ROOT / 'contract' / 'fixtures' / 'tierlist.json'
NOW = datetime(2026, 11, 6, 12, 0, tzinfo=UTC)
CONFIG = TierConfig(
    tiers=(
        Tier('s', 'S', '#ff7f7f', 'The best'),
        Tier('a', 'A', '#ffbf7f'),
        Tier('b', 'B', '#ffdf7f'),
    ),
    stack_depth=3,
    series_total_column='#series_total',
)


def fixture_payload() -> dict[str, Any]:
    library = FakeLibrary(types={'#date_read': 'datetime', '#series_total': 'int'})
    library.values['title'] = {
        1: 'The </script> Problem',
        2: 'Cien años de soledad',
        3: 'Alpha',
        4: 'Bravo',
        5: 'Owned Unread',
        6: 'Unread Excluded',
        7: 'Another S',
        8: 'Zulu',
        9: 'Earthsea One',
    }
    library.values['#tier'] = {1: 's', 2: 's', 3: 'a', 4: 'a', 6: '', 7: 's', 8: '', 9: 'b'}
    library.values['#date_read'] = {
        1: datetime(2024, 1, 10, 20, 0),
        2: date(2024, 2, 20),
        3: date(2023, 5, 1),
        7: datetime(2024, 1, 10, 20, 0),
        8: date(2021, 1, 1),
    }
    library.values['series'] = {2: 'Dune', 3: 'Dune', 5: 'Dune', 9: 'Earthsea'}
    library.values['series_index'] = {2: 2.0, 3: 3.0, 5: 4.0, 9: 1.0}
    library.values['#series_total'] = {2: 7}
    library.values['authors'] = {1: ('Ann Author',), 2: ('Gabriel García Márquez',), 3: ('Frank Herbert',)}
    library.values['rating'] = {1: 9, 2: 10}
    library.values['tags'] = {1: ('mystery', 'classic'), 2: ('magical realism',)}
    library.values['comments'] = {1: '<p>A <b>tense</b> tale &amp; more.</p><script>x()</script>'}
    prefs = FakePrefs({TIER_CONFIG_KEY: CONFIG.to_dict(), SERIES_TIER_OVERRIDES_KEY: {'Dune': 'b'}})
    app = TierList(library, prefs, lambda: NOW.date(), lambda: NOW, covers=FakeCovers(with_cover={1, 2, 3, 7}))
    request = CompileRequest('library', tuple(range(1, 10)), 'Fixture Library', '0.1.0')
    return app.compile(request).to_dict()


class Validator(Protocol):
    """The slice of jsonschema's validator the test calls, so pyright stays strict without stubs."""

    def validate(self, instance: object) -> None: ...


def test_payload_validates_against_the_schema() -> None:
    schema: dict[str, Any] = json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
    validator = cast(Validator, Draft202012Validator(schema, format_checker=FormatChecker()))

    validator.validate(fixture_payload())


def test_payload_matches_the_checked_in_fixture() -> None:
    payload = fixture_payload()

    if os.environ.get('UPDATE_FIXTURE') == '1':
        FIXTURE_PATH.parent.mkdir(parents=True, exist_ok=True)
        FIXTURE_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        return

    assert payload == json.loads(FIXTURE_PATH.read_text(encoding='utf-8'))
