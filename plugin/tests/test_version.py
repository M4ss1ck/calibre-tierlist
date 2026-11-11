"""The three version sources agree: entry point, pyproject and the release manifest.

`calibre_entry.py` imports calibre, so it is parsed with `ast`, never imported.
"""

import ast
import json
import tomllib
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
ROOT = PLUGIN.parent
ENTRY = PLUGIN / 'calibre_entry.py'
PYPROJECT = PLUGIN / 'pyproject.toml'
MANIFEST = ROOT / '.release-please-manifest.json'


def entry_version() -> tuple[int, ...]:
    """The version tuple on TierListPlugin, read without executing the module."""
    tree = ast.parse(ENTRY.read_text(encoding='utf-8'))
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef) or node.name != 'TierListPlugin':
            continue
        for stmt in node.body:
            if not isinstance(stmt, ast.Assign):
                continue
            if not any(isinstance(t, ast.Name) and t.id == 'version' for t in stmt.targets):
                continue
            values: tuple[object, ...] = ast.literal_eval(stmt.value)
            assert isinstance(values, tuple), values
            parts: list[int] = []
            for part in values:
                assert isinstance(part, int) and not isinstance(part, bool), values
                parts.append(part)
            return tuple(parts)
    raise AssertionError('TierListPlugin.version not found')


def pyproject_version() -> tuple[int, ...]:
    with PYPROJECT.open('rb') as fh:
        raw: str = tomllib.load(fh)['project']['version']
    return tuple(int(part) for part in raw.split('.'))


def manifest_version() -> tuple[int, ...]:
    raw: str = json.loads(MANIFEST.read_text(encoding='utf-8'))['.']
    return tuple(int(part) for part in raw.split('.'))


def test_entry_version_matches_pyproject() -> None:
    assert entry_version() == pyproject_version()


def test_entry_version_matches_release_manifest() -> None:
    assert entry_version() == manifest_version()
