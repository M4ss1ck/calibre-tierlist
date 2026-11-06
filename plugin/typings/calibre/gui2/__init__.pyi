from typing import Any

gprefs: Any

class Application:
    def __init__(self, args: Any = ..., force_calibre_style: bool = ..., headless: bool = ...) -> None: ...

def question_dialog(parent: Any, title: str, msg: str, *args: Any, **kwargs: Any) -> bool: ...
def error_dialog(parent: Any, title: str, msg: str, *args: Any, **kwargs: Any) -> Any: ...
def info_dialog(
    parent: Any,
    title: str,
    msg: str,
    det_msg: str = ...,
    show: bool = ...,
    show_copy_button: bool = ...,
    only_copy_details: bool = ...,
) -> Any: ...
