"""Emblems: the cover grid rule and icon file names that show each Book's Tier on its cover."""

import hashlib
from collections.abc import Sequence
from typing import cast

from .tiers import Tier

EMBLEM_DESIGN_VERSION = 1
MARKER = 'program:\n# tierlist-emblem'

Rule = tuple[str, str, str]


def icon_name(tier: Tier) -> str:
    """The icon file name for one Tier: it changes with its label and colour, and with the design version."""
    key = '\0'.join((tier.label, tier.colour.lower(), str(EMBLEM_DESIGN_VERSION)))
    return f'tierlist_{hashlib.sha1(key.encode()).hexdigest()[:12]}.png'


def template_literal(text: str) -> str:
    """One calibre template string literal for text, which is raw: it never escapes a quote."""
    if "'" not in text:
        return f"'{text}'"
    if '"' not in text:
        return f'"{text}"'
    pieces = ', "\'", '.join(f"'{piece}'" for piece in text.split("'"))
    return f'strcat({pieces})'


def emblem_rule(column: str, tiers: Sequence[Tier]) -> Rule:
    """The one marked rule that names the icon of the Tier each book has, or none."""
    if not tiers:
        return ('emblem', column, MARKER + "\n''")
    lines = [MARKER, f'v = field({template_literal(column)});', _body(tiers)]
    return ('emblem', column, '\n'.join(lines))


def is_ours(rule: Sequence[object]) -> bool:
    """Whether a calibre rule is one of ours: a triple whose template starts with MARKER."""
    return len(rule) == 3 and isinstance(rule[2], str) and rule[2].startswith(MARKER)


def merge_rules(rules: Sequence[Sequence[str]], ours: Rule | None) -> list[Rule]:
    """The rules with ours in the first marked rule's place (or appended), later marked rules dropped."""
    merged: list[Rule] = []
    placed = False
    for rule in rules:
        if is_ours(rule):
            if not placed and ours is not None:
                merged.append(ours)
            placed = True
            continue
        merged.append(cast('Rule', tuple(rule)))
    if not placed and ours is not None:
        merged.append(ours)
    return merged


def _body(tiers: Sequence[Tier]) -> str:
    head = f"if v == {template_literal(tiers[0].id)} then '{icon_name(tiers[0])}'"
    rest = ' '.join(f"elif v == {template_literal(tier.id)} then '{icon_name(tier)}'" for tier in tiers[1:])
    return f"{head} {rest} else '' fi" if rest else f"{head} else '' fi"
