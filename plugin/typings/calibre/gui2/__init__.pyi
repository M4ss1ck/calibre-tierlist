from typing import Any

gprefs: Any

class Application:
    def __init__(self, args: Any = ..., force_calibre_style: bool = ..., headless: bool = ...) -> None: ...

def question_dialog(parent: Any, title: str, msg: str, *args: Any, **kwargs: Any) -> bool: ...
def error_dialog(parent: Any, title: str, msg: str, *args: Any, **kwargs: Any) -> Any: ...
def choose_save_file(
    window: Any,
    name: str,
    title: str,
    filters: Any = ...,
    all_files: bool = ...,
    initial_path: Any = ...,
    initial_filename: Any = ...,
) -> str | None: ...
def open_local_file(path: str) -> Any: ...
def info_dialog(
    parent: Any,
    title: str,
    msg: str,
    det_msg: str = ...,
    show: bool = ...,
    show_copy_button: bool = ...,
    only_copy_details: bool = ...,
) -> Any: ...
