from __future__ import annotations
import json
from abc import ABC, abstractmethod
from datetime import UTC, tzinfo
from typing import Any

from .record import LogRecord

class Formatter(ABC):
    """
    Base class for all log formatters.
    """

    @abstractmethod
    def format(self, record: LogRecord) -> str:
        """
        Convert a LogRecord into its string representation.
        """
        raise NotImplementedError

class DefaultFormatter(Formatter):
    """
    Human-readable log formatter.
    """

    __slots__ = (
        "_timestamp_format",
        "_tzinfo",
        "_include_caller",
    )

    def __init__(
        self,
        *,
        timestamp_format: str = "%Y-%m-%d %H:%M:%S.%f %Z",
        tzinfo: tzinfo = UTC,
        include_caller: bool = True,
    ) -> None:
        self._timestamp_format = timestamp_format
        self._tzinfo = tzinfo
        self._include_caller = include_caller

    def format(self, record: LogRecord) -> str:
        timestamp = record.timestamp.astimezone(
            self._tzinfo
        ).strftime(self._timestamp_format)

        parts = [
            timestamp,
            f"[{record.level.name}]",
            f"[{record.logger_name}]",
            record.message,
        ]

        if self._include_caller:
            parts.append(
                f"({record.caller.file_path}:{record.caller.line_number})"
            )

        if record.extra:
            parts.append(
                " ".join(
                    f"{key}={value!r}"
                    for key, value in record.extra.items()
                )
            )

        text = " ".join(parts)

        if record.exception is not None:
            text = f"{text}\n{record.exception.format()}"

        return text

class JsonFormatter(Formatter):
    """
    Formats LogRecord instances as JSON.
    """

    __slots__ = ("_include_caller",)

    def __init__(
        self,
        *,
        include_caller: bool = True,
    ) -> None:
        self._include_caller = include_caller

    def format(self, record: LogRecord) -> str:
        data: dict[str, Any] = {
            "timestamp": record.timestamp.isoformat(),
            "level": record.level.name,
            "logger": record.logger_name,
            "message": record.message,
            "process_id": record.process_id,
            "thread_id": record.thread_id,
            "extra": dict(record.extra),
        }

        if self._include_caller:
            data["caller"] = {
                "file": record.caller.file_path,
                "function": record.caller.function_name,
                "line": record.caller.line_number,
            }

        if record.exception is not None:
            data["exception"] = {
                "type": record.exception.exception_type,
                "message": record.exception.message,
                "traceback": record.exception.format(),
            }

        return json.dumps(
            data,
            default=repr,
            ensure_ascii=False,
        )

class ColoredFormatter(DefaultFormatter):
    """
    Human-readable formatter with ANSI colors based on log level.
    """

    __slots__ = ("_colors", "_reset")

    _RESET = "\033[0m"

    _DEFAULT_COLORS = {
        "TRACE": "\033[90m",      # Gray
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[35m",  # Magenta
    }

    def __init__(
        self,
        *,
        timestamp_format: str = "%Y-%m-%d %H:%M:%S.%f %Z",
        tzinfo: tzinfo = UTC,
        include_caller: bool = True,
        colors: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            timestamp_format=timestamp_format,
            tzinfo=tzinfo,
            include_caller=include_caller,
        )

        self._colors = (
            dict(colors)
            if colors is not None
            else self._DEFAULT_COLORS.copy()
        )
        self._reset = self._RESET

    def format(self, record: LogRecord) -> str:
        message = super().format(record)

        color = self._colors.get(record.level.name)

        if color is None:
            return message

        return f"{color}{message}{self._reset}"