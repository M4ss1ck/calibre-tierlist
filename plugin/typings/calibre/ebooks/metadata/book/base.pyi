from typing import Any

class Metadata:
    title: str
    authors: list[str]
    series: str | None
    series_index: float | None
    rating: int | None
    tags: list[str]
    comments: str | None
    def __init__(self, title: str, authors: list[str], *args: Any, **kwargs: Any) -> None: ...
