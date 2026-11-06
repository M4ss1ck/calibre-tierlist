"""A minimal fake action and job manager that run a calibre job synchronously."""

from typing import Any


class FakeStatusBar:
    """Records the messages the compile job posts to the status bar."""

    def __init__(self) -> None:
        self.messages: list[tuple[str, int]] = []

    def show_message(self, message: str, timeout: int) -> None:
        self.messages.append((message, timeout))


class FakeJobManager:
    """Runs each threaded job on this thread, the way one worker does."""

    def __init__(self) -> None:
        self.jobs: list[Any] = []

    def run_threaded_job(self, job: Any) -> None:
        self.jobs.append(job)
        job.start_work()


class FakeJobGui:
    """The slice of calibre's main window the compile job touches."""

    def __init__(self, db: Any) -> None:
        self.current_db = db
        self.status_bar = FakeStatusBar()
        self.job_manager = FakeJobManager()
        self.exceptions: list[tuple[Any, Any]] = []

    def job_exception(self, job: Any, dialog_title: Any = None) -> None:
        self.exceptions.append((job, dialog_title))


class FakeJobAction:
    """The slice of the Tier List action the compile job touches."""

    def __init__(self, db: Any) -> None:
        self.gui = FakeJobGui(db)
