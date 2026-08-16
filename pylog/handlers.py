from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from queue import Queue
from threading import Event, Lock, Thread
from typing import TextIO

from .formatter import DefaultFormatter, Formatter
from .record import LogRecord

class Handler(ABC):
    """
    Base class for all log handlers.
    """

    __slots__ = ("_formatter", "_lock")

    def __init__(
        self,
        formatter: Formatter | None = None,
    ) -> None:
        self._formatter = formatter or DefaultFormatter()
        self._lock = Lock()

    @property
    def formatter(self) -> Formatter:
        return self._formatter

    @formatter.setter
    def formatter(self, formatter: Formatter) -> None:
        self._formatter = formatter

    def emit(self, record: LogRecord) -> None:
        """
        Thread-safe wrapper around write().
        """

        message = self._formatter.format(record)

        with self._lock:
            self.write(message)

    def close(self) -> None:
        """
        Release any resources held by the handler.
        """
        pass

    @abstractmethod
    def write(self, message: str) -> None:
        """
        Write a formatted log message.
        """
        raise NotImplementedError

class ConsoleHandler(Handler):
    """
    Writes logs to stdout.
    """

    __slots__ = ()

    def write(self, message: str) -> None:
        print(message)

class FileHandler(Handler):
    """
    Writes logs to a file.
    """

    __slots__ = ("_path", "_encoding", "_stream")

    def __init__(
        self,
        path: str | Path,
        *,
        formatter: Formatter | None = None,
        encoding: str = "utf-8",
    ) -> None:
        super().__init__(formatter)

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

    The caller only places the LogRecord into a queue.
    Formatting and actual I/O happen in the worker thread.
    """

    __slots__ = (
        "_handler",
        "_queue",
        "_stop_event",
        "_worker",
        "_closed",
    )

    def __init__(
        self,
        handler: Handler,
        *,
        max_queue_size: int = 10_000,
    ) -> None:
        if max_queue_size <= 0:
            raise ValueError(
                "max_queue_size must be greater than zero"
            )

        super().__init__()

        self._handler = handler
        self._queue: Queue[LogRecord | None] = Queue(
            maxsize=max_queue_size
        )
        self._stop_event = Event()
        self._closed = False

        self._worker = Thread(
            target=self._worker_loop,
            name="pylog-handler",
            daemon=False,
        )
        self._worker.start()

    def emit(self, record: LogRecord) -> None:
        """
        Queue the record for background processing.
        """

        if self._closed:
            raise RuntimeError(
                "Cannot emit to a closed AsyncHandler"
            )

        self._queue.put(record)

    def write(self, message: str) -> None:
        """
        AsyncHandler does not write directly.

        Records are processed by the worker thread.
        """
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
        """
        Wait until all queued records have been processed.
        """
        self._queue.join()

    def close(self) -> None:
        """
        Gracefully stop the worker after processing queued records.
        """

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