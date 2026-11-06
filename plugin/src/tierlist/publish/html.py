"""Render Tier List Data into the single offline HTML file."""

import json
from pathlib import Path

from ..compile import TierListData

MARKER = '__TIERLIST_DATA__'


def render_html(template: str, data: TierListData) -> str:
    """Embed the JSON payload at the template's single marker, safe inside a script tag."""
    if template.count(MARKER) != 1:
        raise ValueError(f'template must contain {MARKER} exactly once')
    payload = json.dumps(data.to_dict(), ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    return template.replace(MARKER, payload)


def write_html(template: str, data: TierListData, path: Path) -> int:
    """Render, write the file as UTF-8, and return its size in bytes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_html(template, data), encoding='utf-8')
    return path.stat().st_size
