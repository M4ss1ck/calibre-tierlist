from typing import Any

class InterfaceAction:
    name: str
    action_spec: tuple[str | None, str | None, str | None, Any]
    action_type: str
    dont_add_to: frozenset[str]
    priority: int
    gui: Any
    qaction: Any
    menuless_qaction: Any
    def __init__(self, parent: Any, site_customization: Any) -> None: ...
    def genesis(self) -> None: ...
    def create_menu_action(
        self,
        menu: Any,
        unique_name: str,
        text: str,
        icon: Any = None,
        shortcut: Any = None,
        description: Any = None,
        triggered: Any = None,
        shortcut_name: Any = None,
        persist_shortcut: bool = False,
    ) -> Any: ...
    def library_changed(self, db: Any) -> None: ...
    def initialization_complete(self) -> None: ...
    def shutting_down(self) -> None: ...
