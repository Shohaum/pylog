from __future__ import annotations
from abc import ABC, abstractmethod

from .levels import LogLevel
from .record import LogRecord

class Filter(ABC):
    """
    Base class for log filters.

    `pre_filter()` may reject a record before a LogRecord is created.

    `filter()` performs the complete filter operation once a
    LogRecord exists.
    """

    def pre_filter(
        self,
        *,
        level: LogLevel,
        logger_name: str,
    ) -> bool:
        """
        Perform a cheap filter check before LogRecord creation.

        Returning False rejects the record immediately.

        The default implementation returns True because most
        filters require information only available on LogRecord.
        """
        return True

    @abstractmethod
    def filter(self, record: LogRecord) -> bool:
        """
        Filter a fully constructed LogRecord.

        Return True to allow the record to continue.
        Return False to discard the record.
        """
        raise NotImplementedError

class LevelFilter(Filter):
    """
    Allows records at or above a minimum log level.
    """

    __slots__ = ("_level",)

    def __init__(self, level: LogLevel) -> None:
        self._level = level

    def pre_filter(
        self,
        *,
        level: LogLevel,
        logger_name: str,
    ) -> bool:
        return level >= self._level

    def filter(self, record: LogRecord) -> bool:
        return record.level >= self._level

class LoggerNameFilter(Filter):
    """
    Allows records from a specific logger.
    """

    __slots__ = ("_logger_name",)

    def __init__(self, logger_name: str) -> None:
        if not logger_name:
            raise ValueError(
                "logger_name cannot be empty"
            )

        self._logger_name = logger_name

    def pre_filter(
        self,
        *,
        level: LogLevel,
        logger_name: str,
    ) -> bool:
        return logger_name == self._logger_name

    def filter(self, record: LogRecord) -> bool:
        return record.logger_name == self._logger_name

class FunctionFilter(Filter):
    """
    Allows records when the caller function matches.

    This cannot participate in pre-record filtering because
    caller information is only available after LogRecord creation.
    """

    __slots__ = ("_function_name",)

    def __init__(self, function_name: str) -> None:
        if not function_name:
            raise ValueError(
                "function_name cannot be empty"
            )

        self._function_name = function_name

    def filter(self, record: LogRecord) -> bool:
        return (
            record.caller.function_name
            == self._function_name
        )