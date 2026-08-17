from __future__ import annotations
from collections.abc import Iterable, Mapping
from contextlib import AbstractContextManager
from typing import Any

from .context import bind
from .filters import Filter
from .handlers import Handler
from .levels import LogLevel
from .record import LogRecord
from .record_factory import LogRecordFactory

class Logger:
    """
    Main logging interface.

    Loggers form a hierarchy based on dot-separated names.

    Example:

        app
        app.api
        app.api.auth

    A logger inherits its effective level from its parent when
    no explicit level is configured.
    """

    __slots__ = (
        "_name",
        "_level",
        "_handlers",
        "_filters",
        "_record_factory",
        "_parent",
        "_propagate",
    )

    def __init__(
        self,
        *,
        name: str,
        record_factory: LogRecordFactory,
        level: LogLevel | None = None,
        handlers: Iterable[Handler] | None = None,
        filters: Iterable[Filter] | None = None,
        parent: Logger | None = None,
        propagate: bool = True,
    ) -> None:
        if not name and parent is not None:
            raise ValueError(
                "Only the root logger can have an empty name."
            )

        self._name = name
        self._level = level
        self._record_factory = record_factory

        self._handlers = (
            list(handlers)
            if handlers is not None
            else []
        )

        self._filters = (
            list(filters)
            if filters is not None
            else []
        )

        self._parent = parent
        self._propagate = propagate

    @property
    def name(self) -> str:
        return self._name

    @property
    def level(self) -> LogLevel | None:
        """
        Return the logger's explicitly configured level.

        None means the logger inherits its level from its parent.
        """
        return self._level

    @level.setter
    def level(self, level: LogLevel | None) -> None:
        self._level = level

    @property
    def effective_level(self) -> LogLevel:
        """
        Return the level actually used by this logger.
        """
        if self._level is not None:
            return self._level

        if self._parent is not None:
            return self._parent.effective_level

        raise RuntimeError(
            "Logger has no configured level."
        )

    @property
    def parent(self) -> Logger | None:
        return self._parent

    def set_parent(self, parent: Logger | None) -> None:
        self._parent = parent

    @property
    def propagate(self) -> bool:
        return self._propagate

    @propagate.setter
    def propagate(self, value: bool) -> None:
        self._propagate = value

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
        if level < self.effective_level:
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

        self._emit_to_handlers(record)

        if self._propagate and self._parent is not None:
            self._parent._propagate_record(record)

    def _propagate_record(self, record: LogRecord) -> None:
        """
        Deliver an already-created record to this logger's handlers
        and continue propagation.

        The record is not filtered by the parent's logger filters or
        effective level. Handler filters still apply.
        """
        self._emit_to_handlers(record)

        if self._propagate and self._parent is not None:
            self._parent._propagate_record(record)

    def _emit_to_handlers(self, record: LogRecord) -> None:
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