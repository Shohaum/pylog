from __future__ import annotations
from abc import ABC, abstractmethod

from .record import LogRecord

class Filter(ABC):
    """
    Base class for log filters.

    Return True to allow the record to continue.
    Return False to discard the record.
    """

    @abstractmethod
    def filter(self, record: LogRecord) -> bool:
        raise NotImplementedError

class LevelFilter(Filter):
    """
    Allows records at or above a minimum log level.
    """

    __slots__ = ("_level",)

    def __init__(self, level) -> None:
        self._level = level

    def filter(self, record: LogRecord) -> bool:
        return record.level >= self._level

class LoggerNameFilter(Filter):
    """
    Allows records from a specific logger.
    """

    __slots__ = ("_logger_name",)

    def __init__(self, logger_name: str) -> None:
        if not logger_name:
            raise ValueError("logger_name cannot be empty")

        self._logger_name = logger_name

    def filter(self, record: LogRecord) -> bool:
        return record.logger_name == self._logger_name

class FunctionFilter(Filter):
    """
    Allows records when the caller function matches.
    """

    __slots__ = ("_function_name",)

    def __init__(self, function_name: str) -> None:
        if not function_name:
            raise ValueError("function_name cannot be empty")

        self._function_name = function_name

    def filter(self, record: LogRecord) -> bool:
        return record.caller.function_name == self._function_name