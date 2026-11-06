"""Minimal stubs for the Pillow names the plugin imports (Pillow is optional)."""

from typing import Any

def open(fp: Any) -> Image: ...

class Image:
    def save(self, fp: Any, format: str | None = None, **params: Any) -> None: ...
