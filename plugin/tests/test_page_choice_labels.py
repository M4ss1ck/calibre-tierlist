"""Every Page tab combo offers exactly the values Page Defaults accepts, each with a label."""

import builtins

import pytest

from tierlist.calibre_ui import page_labels
from tierlist.page_choices import COVER_SIZES, EMPTY_LANES, GAPS, PAGE_WIDTHS, THEMES


def _identity(text: str) -> str:
    return text


@pytest.fixture(autouse=True)
def gettext(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(builtins, '_', _identity, raising=False)


@pytest.mark.parametrize(
    ('builder', 'allowed'),
    [
        ('theme_choices', THEMES),
        ('page_width_choices', PAGE_WIDTHS),
        ('gap_choices', GAPS),
        ('cover_size_choices', COVER_SIZES),
        ('empty_lane_choices', EMPTY_LANES),
    ],
)
def test_choices_cover_every_allowed_value(builder: str, allowed: tuple[str, ...]) -> None:
    choices = getattr(page_labels, builder)()

    assert tuple(value for value, _label in choices) == allowed
    assert all(label.strip() for _value, label in choices)
