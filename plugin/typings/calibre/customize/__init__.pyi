from collections.abc import Sequence
from typing import Any

class Plugin:
    name: str
    description: str
    author: str
    version: tuple[int, int, int]
    minimum_calibre_version: tuple[int, ...]
    supported_platforms: Sequence[str]
    type: str
    actual_plugin: str | None

class InterfaceActionBase(Plugin):
    actual_plugin_: Any
    def load_actual_plugin(self, gui: Any) -> Any: ...
