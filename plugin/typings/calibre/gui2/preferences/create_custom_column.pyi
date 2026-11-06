from typing import Any

class CreateNewCustomColumn:
    Result: Any
    def __init__(self, gui: Any) -> None: ...
    def must_restart(self) -> bool: ...
    def create_column(
        self,
        lookup_name: str,
        column_heading: str,
        datatype: str,
        is_multiple: bool,
        display: Any = ...,
        generate_unused_lookup_name: bool = False,
        freeze_lookup_name: bool = True,
    ) -> tuple[Any, str]: ...
