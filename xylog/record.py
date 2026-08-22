"""
Immutable representation of a single loging event.
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping

from .exception_info import ExceptionInfo
from .caller_info import CallerInfo
from .levels import LogLevel

@dataclass(frozen=True, slots=True)
class LogRecord:
    """
    Immutable representation of a logging event.

    A LogRecord contains only data.
    It knows nothing about formatting, handlers,
    output destinations, or record creation.
    """

    timestamp: datetime
    level: LogLevel
    logger_name: str
    message: str
    process_id: int
    thread_id: int
    # file_path: str
    # function_name: str
    # line_number: int
    caller: CallerInfo
    exception: ExceptionInfo | None
    extra: Mapping[str, Any]

    def __post_init__(self) -> None:
        self._validate_identity()
        self._validate_timestamp()
        # self._validate_location()
        self._validate_runtime()
        self._validate_extra()

    def _validate_identity(self) -> None:
        if not isinstance(self.level, LogLevel):
            raise TypeError(
                f"Expected LogLevel, got {type(self.level).__name__}"
            )

        if not self.logger_name:
            raise ValueError("logger_name cannot be empty")
        
        if self.logger_name.strip() != self.logger_name:
            raise ValueError("logger_name cannot contain leading or trailing whitespace")
        
        if not self.message:
            raise ValueError("message connot be empty")

    def _validate_timestamp(self) -> None:
        """Timestamp must be timexone-aware and stored in UTC."""

        if self.timestamp.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")

        if self.timestamp.utcoffset() != timezone.utc.utcoffset(self.timestamp):
            raise ValueError("timestamp must be in UTC")
        
    # def _validate_location(self) -> None:
    #     if not self.file_path:
    #         raise ValueError("file_path cannot be empty")

    #     if not self.function_name:
    #         raise ValueError("function_name cannot be empty")

    #     if self.line_number <= 0:
    #         raise ValueError("line_number must be greater than zero")
    
    def _validate_runtime(self) -> None:
        if self.process_id <= 0:
            raise ValueError("process_id must be greater than zero")

        if self.thread_id <= 0:
            raise ValueError("thread_id must be greater than zero")
        
    def _validate_extra(self) -> None:
        if self.extra is None:
            raise ValueError("extra cannot be None")