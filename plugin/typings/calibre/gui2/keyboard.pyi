from typing import Any

class Manager:
    shortcuts: dict[str, dict[str, Any]]
    keys_map: dict[str, Any]
    groups: dict[str, list[str]]
    def __init__(self, parent: Any = None, config_name: str = ...) -> None: ...
    def register_shortcut(
        self,
        unique_name: str,
        name: str,
        default_keys: Any = ...,
        description: Any = None,
        action: Any = None,
        group: Any = None,
        persist_shortcut: bool = False,
    ) -> None: ...
    def unregister_shortcut(self, unique_name: str) -> None: ...
    def finalize(self) -> None: ...
