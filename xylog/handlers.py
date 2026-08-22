from __future__ import annotations
import sys
from abc import ABC, abstractmethod
from collections.abc import Iterable
from pathlib import Path
from queue import Queue
from threading import Lock, Thread
from typing import TextIO

from .filters import Filter
from .formatter import DefaultFormatter, Formatter
from .record import LogRecord

class Handler(ABC):
    """
    Base class for all log handlers.
    """

    __slots__ = (
        "_formatter",
        "_lock",
        "_filters",
    )

    def __init__(
        self,
        formatter: Formatter | None = None,
        *,
        filters: Iterable[Filter] | None = None,
    ) -> None:
        self._formatter = formatter or DefaultFormatter()
        self._lock = Lock()
        self._filters = list(filters) if filters is not None else []

    @property
    def formatter(self) -> Formatter:
        return self._formatter

    @formatter.setter
    def formatter(self, formatter: Formatter) -> None:
        self._formatter = formatter

    @property
    def supports_color(self) -> bool:
        return False

    def add_filter(self, filter_: Filter) -> None:
        self._filters.append(filter_)

    def remove_filter(self, filter_: Filter) -> None:
        self._filters.remove(filter_)

    def _should_emit(self, record: LogRecord) -> bool:
        return all(
            filter_.filter(record)
            for filter_ in self._filters
        )

    def emit(self, record: LogRecord) -> None:
        """
        Filter, format, and write a record.
        """

        if not self._should_emit(record):
            return

        message = self._formatter.format(
            record,
            color=self.supports_color,
        )

        with self._lock:
            self.write(message)

    def close(self) -> None:
        pass

    @abstractmethod
    def write(self, message: str) -> None:
        raise NotImplementedError

class ConsoleHandler(Handler):
    """
    Writes logs to stdout.
    """

    __slots__ = ()

    @property
    def supports_color(self) -> bool:
        return bool(
            getattr(sys.stdout, "isatty", lambda: False)()
        )

    def write(self, message: str) -> None:
        print(message)

class FileHandler(Handler):
    """
    Writes logs to a file.
    """

    __slots__ = (
        "_path",
        "_encoding",
        "_stream",
    )

    def __init__(
        self,
        path: str | Path,
        *,
        formatter: Formatter | None = None,
        encoding: str = "utf-8",
        filters: Iterable[Filter] | None = None,
    ) -> None:
        super().__init__(
            formatter,
            filters=filters,
        )

        self._path = Path(path)
        self._encoding = encoding

        self._path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._stream: TextIO = self._path.open(
            mode="a",
            encoding=self._encoding,
        )

    @property
    def path(self) -> Path:
        return self._path

    def write(self, message: str) -> None:
        self._stream.write(message)
        self._stream.write("\n")
        self._stream.flush()

    def close(self) -> None:
        if not self._stream.closed:
            self._stream.close()

    def __enter__(self) -> "FileHandler":
        return self

    def __exit__(
        self,
        exc_type,
        exc,
        tb,
    ) -> None:
        self.close()

class AsyncHandler(Handler):
    """
    Executes another handler in a background worker thread.
    """

    __slots__ = (
        "_handler",
        "_queue",
        "_worker",
        "_closed",
    )

    def __init__(
        self,
        handler: Handler,
        *,
        max_queue_size: int = 10_000,
        filters: Iterable[Filter] | None = None,
    ) -> None:
        if max_queue_size <= 0:
            raise ValueError(
                "max_queue_size must be greater than zero"
            )

        super().__init__(filters=filters)

        self._handler = handler

        self._queue: Queue[LogRecord | None] = Queue(
            maxsize=max_queue_size
        )

        self._closed = False

        self._worker = Thread(
            target=self._worker_loop,
            name="pylog-handler",
            daemon=False,
        )

        self._worker.start()

    @property
    def supports_color(self) -> bool:
        return self._handler.supports_color

    def emit(self, record: LogRecord) -> None:
        if self._closed:
            raise RuntimeError(
                "Cannot emit to a closed AsyncHandler"
            )

        if not self._should_emit(record):
            return

        self._queue.put(record)

    def write(self, message: str) -> None:
        raise RuntimeError(
            "AsyncHandler.write() should not be called directly"
        )

    def _worker_loop(self) -> None:
        while True:
            record = self._queue.get()

            try:
                if record is None:
                    return

                self._handler.emit(record)

            finally:
                self._queue.task_done()

    def flush(self) -> None:
        self._queue.join()

    def close(self) -> None:
        if self._closed:
            return

        self._closed = True

        self._queue.put(None)
        self._worker.join()

        self._handler.close()

    def __enter__(self) -> "AsyncHandler":
        return self

    def __exit__(
        self,
        exc_type,
        exc,
        tb,
    ) -> None:
        self.close()

class RotatingFileHandler(FileHandler):
    """
    Rotates the log file when it reaches a configured size.
    """

    __slots__ = (
        "_max_bytes",
        "_backup_count",
    )

    def __init__(
        self,
        path: str | Path,
        *,
        max_bytes: int,
        backup_count: int = 5,
        formatter: Formatter | None = None,
        encoding: str = "utf-8",
        filters: Iterable[Filter] | None = None,
    ) -> None:
        if max_bytes <= 0:
            raise ValueError(
                "max_bytes must be greater than zero"
            )

        if backup_count < 0:
            raise ValueError(
                "backup_count cannot be negative"
            )

        super().__init__(
            path,
            formatter=formatter,
            encoding=encoding,
            filters=filters,
        )

        self._max_bytes = max_bytes
        self._backup_count = backup_count

    def write(self, message: str) -> None:
        data = f"{message}\n"
        size = len(data.encode(self._encoding))

        if self._stream.tell() + size > self._max_bytes:
            self._rotate()

        self._stream.write(data)
        self._stream.flush()

    def _rotate(self) -> None:
        self._stream.close()

        if self._backup_count > 0:
            for index in range(
                self._backup_count - 1,
                0,
                -1,
            ):
                source = self._path.with_name(
                    f"{self._path.name}.{index}"
                )
                destination = self._path.with_name(
                    f"{self._path.name}.{index + 1}"
                )

                if source.exists():
                    source.replace(destination)

            rotated = self._path.with_name(
                f"{self._path.name}.1"
            )

            if self._path.exists():
                self._path.replace(rotated)

        self._stream = self._path.open(
            mode="a",
            encoding=self._encoding,
        )