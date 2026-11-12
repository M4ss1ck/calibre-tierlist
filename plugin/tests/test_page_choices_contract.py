"""The plugin accepts exactly the Page Defaults choices the contract allows, in contract order."""

import json
from pathlib import Path
from typing import Any

import pytest

from tierlist.page_choices import COVER_SIZES, EMPTY_LANES, GAPS, PAGE_WIDTHS, THEMES

SCHEMA = Path(__file__).resolve().parents[2] / 'contract' / 'tierlist.schema.json'


def allowed(key: str) -> list[str]:
    defs: dict[str, Any] = json.loads(SCHEMA.read_text(encoding='utf-8'))['$defs']
    prop: dict[str, Any] = defs['PageDefaults']['properties'][key]
    return defs['Gap']['enum'] if prop.get('$ref') == '#/$defs/Gap' else prop['enum']


@pytest.mark.parametrize(
    ('key', 'values'),
    [
        ('theme', THEMES),
        ('pageWidth', PAGE_WIDTHS),
        ('laneGap', GAPS),
        ('coverGap', GAPS),
        ('coverSize', COVER_SIZES),
        ('emptyLane', EMPTY_LANES),
    ],
)
def test_choices_match_the_contract(key: str, values: tuple[str, ...]) -> None:
    assert list(values) == allowed(key)
