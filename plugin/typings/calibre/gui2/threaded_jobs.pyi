from collections.abc import Callable
from typing import Any

class ThreadedJob:
    failed: bool
    result: Any
    def __init__(
        self,
        type_: str,
        description: str,
        func: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        callback: Callable[[ThreadedJob], None],
        max_concurrent_count: int = ...,
        killable: bool = ...,
        log: Any = ...,
    ) -> None: ...
