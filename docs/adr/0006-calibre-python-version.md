# 0006 calibre's Python version

Status: Accepted
Date: 2026-11-05

## Context

The plugin runs inside calibre's bundled CPython, not the system interpreter, so the language level available to us is set by calibre. Lint and type checks only catch incompatible syntax and stdlib use when their target matches that interpreter.

## Decision

calibre 9.0.0 ships CPython 3.14.2. This was measured on the official isolated 9.0.0 install with `calibre-debug -c 'import sys; print(sys.version)'`, which printed `3.14.2 (main, Dec 10 2025, 18:00:57) [GCC 11.4.0]`. `plugin/pyproject.toml` therefore sets ruff `target-version = "py314"`, with `requires-python = ">=3.14"`.

## Consequences

- Plugin code may use Python 3.14 syntax and stdlib, and ruff rejects anything newer.
- Anything imported at plugin runtime must be stdlib: we cannot install into calibre's interpreter.
- Raising `minimum_calibre_version` means re-measuring its Python and updating the ruff target and this ADR together.
