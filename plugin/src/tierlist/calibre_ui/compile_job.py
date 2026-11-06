"""The calibre background job that compiles the Tier List and opens it."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

from calibre.gui2 import open_local_file
from calibre.gui2.threaded_jobs import ThreadedJob

from ..app import TierList
from ..compile import CompileRequest
from .adapters import tier_list


def scope_book_ids(gui: Any, scope: str) -> tuple[int, ...]:
    """The book ids the Compile Scope covers, sorted."""
    db = gui.current_db
    if scope == 'virtual_library':
        return tuple(sorted(db.new_api.search('', restriction=db.data.get_base_restriction())))
    if scope == 'selection':
        return tuple(sorted(gui.library_view.get_selected_ids()))
    return tuple(sorted(db.new_api.all_book_ids()))


def run_compile(app: TierList, request: CompileRequest, template: str, path: str, log: Callable[[str], None]) -> str:
    """Compile the Tier List to a file through the facade and return its path."""
    app.compile_to_file(request, template, Path(path), log)
    return path


def start_compile(action: Any, request: CompileRequest, template: str, path: str) -> None:
    """Run the compile in calibre's job system, then open the written file."""
    app = tier_list(action.gui.current_db)

    def func(log: Any = None, abort: Any = None, notifications: Any = None) -> None:
        notifications.put((0.0, _('Compiling tier list')))
        run_compile(app, request, template, path, _logger(log))
        notifications.put((1.0, _('Done')))

    def callback(job: ThreadedJob) -> None:
        if job.failed:
            action.gui.job_exception(job, dialog_title=_('Tier List compile failed'))
            return
        open_local_file(path)
        action.gui.status_bar.show_message(_('Tier list written to %s') % path, 5000)

    job = ThreadedJob('tierlist_compile', _('Compile tier list'), func, (), {}, callback)
    action.gui.job_manager.run_threaded_job(job)


def _logger(log: Any) -> Callable[[str], None]:
    def write(line: str) -> None:
        print(line)
        if log is not None:
            log.info(line)

    return write
