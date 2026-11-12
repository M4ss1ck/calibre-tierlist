"""The built zip: entry point at the root, calibre_ui inside, template optional.

Uses the real repo SRC and ENTRY; only the template path is faked.
"""

import zipfile
from pathlib import Path

import build_zip
import pytest


def build(out_dir: Path, monkeypatch: pytest.MonkeyPatch, template: Path) -> zipfile.ZipFile:
    monkeypatch.setattr(build_zip, 'TEMPLATE', template)
    return zipfile.ZipFile(build_zip.build(out_dir / 'tierlist.zip'))


def test_zip_layout(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    with build(tmp_path, monkeypatch, tmp_path / 'no-template.html') as zf:
        names = zf.namelist()
        assert 'plugin-import-name-tierlist.txt' in names
        assert 'calibre_ui/action.py' in names
        assert zf.read('images/icon.png').startswith(b'\x89PNG')
        assert zf.read('__init__.py') == build_zip.ENTRY.read_bytes()
        assert zf.read('__init__.py') != (build_zip.SRC / '__init__.py').read_bytes()
        assert not [name for name in names if '__pycache__' in name]


def test_template_included_when_built(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    template = tmp_path / 'template.html'
    template.write_bytes(b'<html></html>')
    with build(tmp_path, monkeypatch, template) as zf:
        assert zf.read('template.html') == b'<html></html>'


def test_template_absent_when_not_built(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    with build(tmp_path, monkeypatch, tmp_path / 'no-template.html') as zf:
        assert 'template.html' not in zf.namelist()
