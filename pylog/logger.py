from __future__ import annotations
from collections.abc import Iterable, Mapping
from contextlib import AbstractContextManager
from typing import Any

from .context import bind
from .filters import Filter
from .handlers import ConsoleHandler, Handler
from .levels import LogLevel
from .record_factory import LogRecordFactory

class Logger:
    """
    Main logging interface.
    """

    __slots__ = (
        "_name",
        "_level",
        "_handlers",
        "_filters",
        "_record_factory",
    )

    def __init__(
        self,
        *,
        name: str,
        record_factory: LogRecordFactory,
        level: LogLevel = LogLevel.INFO,
        handlers: Iterable[Handler] | None = None,
        filters: Iterable[Filter] | None = None,
    ) -> None:
        if not name:
            raise ValueError("Logger name cannot be empty.")

        self._name = name
        self._record_factory = record_factory
        self._level = level

        self._handlers = (
            list(handlers)
            if handlers is not None
            else [ConsoleHandler()]
        )

        self._filters = (
            list(filters)
            if filters is not None
            else []
        )

    @property
    def name(self) -> str:
        return self._name

    @property
    def level(self) -> LogLevel:
        return self._level

    @level.setter
    def level(self, level: LogLevel) -> None:
        self._level = level

    def add_handler(self, handler: Handler) -> None:
        self._handlers.append(handler)

    def remove_handler(self, handler: Handler) -> None:
        self._handlers.remove(handler)

    def add_filter(self, filter_: Filter) -> None:
        self._filters.append(filter_)

    def remove_filter(self, filter_: Filter) -> None:
        self._filters.remove(filter_)

    def context(
        self,
        **values: Any,
    ) -> AbstractContextManager[None]:
        return bind(**values)

    def log(
        self,
        level: LogLevel,
        message: str,
        *,
        exception: BaseException | None = None,
        extra: Mapping[str, Any] | None = None,
    ) -> None:
        if level < self._level:
            return

        record = self._record_factory.create(
            level=level,
            logger_name=self._name,
            message=message,
            exception=exception,
            extra=extra,
        )

        if not all(
            filter_.filter(record)
            for filter_ in self._filters
        ):
            return

        for handler in self._handlers:
            handler.emit(record)

    def trace(self, message: str, **kwargs: Any) -> None:
        self.log(LogLevel.TRACE, message, **kwargs)

    def debug(self, message: str, **kwargs: Any) -> None:
        self.log(LogLevel.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        self.log(LogLevel.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        self.log(LogLevel.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        self.log(LogLevel.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        self.log(LogLevel.CRITICAL, message, **kwargs)

    def exception(
        self,
        message: str,
        exception: BaseException,
        **kwargs: Any,
    ) -> None:
        self.error(
            message,
            exception=exception,
            **kwargs,
        )

    def close(self) -> None:
        for handler in self._handlers:
            handler.close()