from pathlib import Path

import pytest
from check_file_length import main


def make(path: Path, lines: int) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(''.join(f'x{i} = {i}\n' for i in range(lines)), encoding='utf-8')
    return path


def test_hard_cap_file_passes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    make(tmp_path / 'ok.py', 150)
    assert main([str(tmp_path)]) == 0
    assert 'ERROR' not in capsys.readouterr().out


def test_hard_cap_exceeded_fails(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    make(tmp_path / 'long.py', 151)
    assert main([str(tmp_path)]) == 1
    assert 'ERROR' in capsys.readouterr().out


def test_soft_cap_warns_but_passes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    make(tmp_path / 'soft.svelte', 101)
    assert main([str(tmp_path)]) == 0
    assert 'WARN' in capsys.readouterr().out


def test_node_modules_is_skipped(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    make(tmp_path / 'node_modules' / 'dep' / 'long.ts', 400)
    assert main([str(tmp_path)]) == 0
    assert 'ERROR' not in capsys.readouterr().out


def test_the_generated_contract_file_is_skipped(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    generated = tmp_path / 'web' / 'src' / 'contract' / 'tierlist.ts'
    generated.parent.mkdir(parents=True)
    generated.write_text('/* Generated from a schema. Do not edit. */\n' + 'x\n' * 400, encoding='utf-8')
    assert main([str(tmp_path)]) == 0
    assert 'ERROR' not in capsys.readouterr().out


def test_a_generated_marker_does_not_exempt_another_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    marked = tmp_path / 'types.ts'
    marked.write_text('/* Generated from a schema. Do not edit. */\n' + 'x\n' * 400, encoding='utf-8')
    assert main([str(tmp_path)]) == 1
    assert 'ERROR' in capsys.readouterr().out
