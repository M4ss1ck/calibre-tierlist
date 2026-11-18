"""Emblems: the marked calibre rule, its template literals, and the icon file name one Tier gets."""

import pytest

from tierlist import emblems
from tierlist.emblems import (
    EMBLEM_DESIGN_VERSION,
    MARKER,
    emblem_rule,
    icon_name,
    is_ours,
    merge_rules,
    template_literal,
)
from tierlist.tiers import Tier

S = Tier('s', 'S', '#ff7f7f')
A = Tier('a', 'A', '#ffbf7f')
S_ICON = 'tierlist_ee897c59a9db.png'
A_ICON = 'tierlist_6ffc5d4fff7f.png'
OURS = emblem_rule('#tier', (S,))
OLDER_OURS = ('emblem', '#tier', MARKER + "\n''")
FOREIGN_HEAD = ('icon', '#other', 'program:\n# other')
FOREIGN_TAIL = ('icon', '#more', 'x')


def test_marker_and_design_version_are_frozen() -> None:
    assert MARKER == 'program:\n# tierlist-emblem'
    assert EMBLEM_DESIGN_VERSION == 1


def test_rule_for_two_tiers_is_exact_and_empty_is_only_the_marker() -> None:
    expected = (
        "program:\n# tierlist-emblem\nv = field('#tier');\n"
        f"if v == 's' then '{S_ICON}' elif v == 'a' then '{A_ICON}' else '' fi"
    )
    assert emblem_rule('#tier', (S, A)) == ('emblem', '#tier', expected)
    assert emblem_rule('#tier', ()) == ('emblem', '#tier', MARKER + "\n''")
    tiers = (S, A, Tier('b', 'B', '#ffdf7f'))
    for count in (1, 2, 3):
        template = emblem_rule('#tier', tiers[:count])[2]
        assert template.count(' then ') == count
        assert template.endswith("else '' fi")


@pytest.mark.parametrize(
    ('text', 'expected'),
    [
        ('', "''"),
        ('plain', "'plain'"),
        ("a'b", '"a\'b"'),
        ('a"b', "'a\"b'"),
        ('a\'b"c', "strcat('a', \"'\", 'b\"c')"),
    ],
)
def test_template_literal_quotes_raw_text(text: str, expected: str) -> None:
    assert template_literal(text) == expected


def test_is_ours_reads_the_marker_not_the_kind() -> None:
    assert is_ours(OURS)
    assert is_ours(('icon', '#tier', MARKER + '\nx'))
    assert not is_ours(FOREIGN_HEAD)
    assert not is_ours(('emblem', '#tier', MARKER, 'extra'))
    assert not is_ours(('emblem', '#tier', 7))


def test_merge_replaces_only_the_first_marked_rule_in_place() -> None:
    rules = [FOREIGN_HEAD, OLDER_OURS, FOREIGN_TAIL]
    assert merge_rules(rules, OURS) == [FOREIGN_HEAD, OURS, FOREIGN_TAIL]
    doubled = [FOREIGN_HEAD, OLDER_OURS, FOREIGN_TAIL, OLDER_OURS]
    assert merge_rules(doubled, OURS) == [FOREIGN_HEAD, OURS, FOREIGN_TAIL]
    assert merge_rules([FOREIGN_HEAD], OURS) == [FOREIGN_HEAD, OURS]
    assert merge_rules([FOREIGN_HEAD, OURS, FOREIGN_TAIL], OURS) == [FOREIGN_HEAD, OURS, FOREIGN_TAIL]


def test_merge_removes_our_rule_on_none() -> None:
    assert merge_rules([FOREIGN_HEAD, OLDER_OURS, FOREIGN_TAIL], None) == [FOREIGN_HEAD, FOREIGN_TAIL]
    assert merge_rules([OLDER_OURS, OLDER_OURS], None) == []


def test_icon_name_ignores_id_and_colour_case() -> None:
    assert icon_name(S) == S_ICON
    assert icon_name(S) == icon_name(Tier('z', 'S', '#ff7f7f'))
    assert icon_name(S) == icon_name(Tier('s', 'S', '#FF7F7F'))


def test_icon_name_changes_with_label_colour_and_design_version(monkeypatch: pytest.MonkeyPatch) -> None:
    assert icon_name(S) != icon_name(Tier('s', 'Masterpiece', '#ff7f7f'))
    assert icon_name(S) != icon_name(Tier('s', 'S', '#ffbf7f'))
    before = icon_name(S)
    monkeypatch.setattr(emblems, 'EMBLEM_DESIGN_VERSION', EMBLEM_DESIGN_VERSION + 1)
    assert icon_name(S) != before
