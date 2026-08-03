from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from threading import Lock
from typing import TextIO

from .formatter import Formatter, DefaultFormatter
from .record import LogRecord

class Handler(ABC):
    """
    Base class for all log handlers.
    """

    __slots__ = ("_formatter", "_lock")

    def __init__(
        self,
        formatter: Formatter | None = None
    ) -> None:
        self._formatter = formatter or DefaultFormatter()
        self._lock = Lock()

    
    @property
    def formatter(self) -> Formatter:
        return self._formatter

    @formatter.setter
    def formmater(self, formmater: Formatter) -> None:
        self._formatter = formmater
    
    def emit(self, record: LogRecord) -> None:
        """
        Thread-safe wrapper around write().
        """

        message = self._formatter.format(record)

        with self._lock:
            self.write(message)
        
    @abstractmethod
    def write(self, message: str) -> None:
        """
        Write a formatted log message.
        """
        raise NotImplementedError

class ConsoleHandler(Handler):
    """
    Writes logs to stdout
    """
    __slots__ = ()

    def write(self, message: str) -> None:
        print(message)
    

class FileHandler(Handler):
    """
    Writes log to a file
    """
    __slots__ = ("_path", "_encoding", "_stream")

    def __init__(
        self,
        path: str | Path,
        *,
        formmater: Formatter | None = None,
        encoding: str = "utf-8"
    ) -> None:
        super().__init__(formmater)

        self._path = Path(path)
        self._encoding = encoding

        self._path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self._stream: TextIO = self._path.open(
            mode="a",
            encoding=self._encoding
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
        tb
    ) -> None:
        self.close()