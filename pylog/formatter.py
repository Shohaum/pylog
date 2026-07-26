from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import timezone

from .record import LogRecord

class Formatter(ABC):
    """
    Base class for all log formatters.
    """
    
    @abstractmethod
    def format(self, record: LogRecord) -> str:
        """
        Convert a LogRecord info its string representation.
        """
        raise NotImplementedError

class DefaultFormatter(Formatter):
    """
    Default human-readable formatter.
    """

    __slots__ = (
        "_timestampt_format",
        "_include_caller"
    )

    def __init__(self, *, timestamp_format: str = "%Y-%m-%d %H:%M:%S.%f %Z", include_caller: bool = True) -> None:
        self._timestamp_format = timestamp_format
        self._include_caller = include_caller

    def format(self, record: LogRecord) -> str:
        timestamp = record.timestamp.astimezone(
            timezone.utc
        ).strftime(self._timestamp_format)

        parts = [
            timestamp,
            f"[{record.level.name}]",
            f"[{record.logger_name}]",
            record.message
        ]

        if self._include_caller:
            parts.append(
                f"({record.caller.file_path}:{record.caller.line_number})"
            )

        text = " ".join(parts)

        if record.exception is not None:
            text += "\n"
            text += record.exception.format()

        return text