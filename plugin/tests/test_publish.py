"""Publish through the facade: safe JSON embedding and the written file."""

import json
import re
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
from fakes import FakeLibrary, FakePrefs

from tierlist.app import TierList
from tierlist.compile import Book, CompileRequest, Generated, Lane, TierListData
from tierlist.publish import MARKER, render_html
from tierlist.tiers import DEFAULT_TIER_CONFIG

NOW = datetime(2026, 11, 6, 12, 0, tzinfo=UTC)
TODAY = date(2026, 11, 6)
PREFIX = '<script>const DATA = '
SUFFIX = ';</script>'
LOG_LINE = re.compile(r'^Tier List compiled: \d+ books, \d+ series in \d+\.\d{2}s, \d+ bytes -> .+$')


def sample_data() -> TierListData:
    tiers = DEFAULT_TIER_CONFIG.tiers
    lanes = (Lane('s', (1,)),) + tuple(Lane(tier.id, ()) for tier in tiers[1:]) + (Lane(None, ()),)
    books = (Book(1, 'The </script> Problem', 's', date(2024, 1, 1)),)
    return TierListData(Generated(NOW, 'Lib', 'library', '0.1.0'), tiers, lanes, books)


def test_render_html_keeps_the_payload_safe_inside_a_script_tag() -> None:
    data = sample_data()

    html = render_html(f'{PREFIX}{MARKER}{SUFFIX}', data)
    payload = html.removeprefix(PREFIX).removesuffix(SUFFIX)

    assert '</' not in payload
    assert json.loads(payload.replace('<\\/', '</')) == data.to_dict()


def test_render_html_rejects_a_template_without_the_marker() -> None:
    with pytest.raises(ValueError):
        render_html('<html></html>', sample_data())


def test_render_html_rejects_a_doubled_marker() -> None:
    with pytest.raises(ValueError):
        render_html(MARKER + MARKER, sample_data())


def test_compile_to_file_writes_the_file_and_logs_once(tmp_path: Path) -> None:
    library = FakeLibrary(types={'#date_read': 'datetime'})
    library.values['title'] = {1: 'One'}
    library.values['#tier'] = {1: 's'}
    library.values['series'] = {1: 'Dune'}
    app = TierList(library, FakePrefs(), lambda: TODAY, lambda: NOW)
    logs: list[str] = []
    path = tmp_path / 'out' / 'tierlist.html'

    app.compile_to_file(CompileRequest('library', (1,), 'Lib', '0.1.0'), f'{PREFIX}{MARKER}{SUFFIX}', path, logs.append)

    assert path.exists()
    assert '"title":"One"' in path.read_text(encoding='utf-8')
    assert len(logs) == 1
    assert LOG_LINE.match(logs[0])
