from __future__ import annotations
from typing import Iterable

from .caller_info import CallerInspector
from .handlers import ConsoleHandler, Handler
from .filters import Filter
from .levels import LogLevel
from .logger import Logger
from .record_factory import LogRecordFactory

class LoggerManager:
    """
    Creates and manages Logger instances.

    Loggers are cached by name so repeated calls to get_logger()
    return the same Logger instance.
    """

    __slots__ = (
        "_record_factory",
        "_loggers",
        "_default_level",
        "_default_handlers"
    )

    def __init__(
        self,
        *,
        default_level: LogLevel = LogLevel.INFO,
        default_handlers: Iterable[Handler] | None = None
    )  -> None:
    
        inspector = CallerInspector()

        self._record_factory = LogRecordFactory(inspector)
        self._default_level = default_level
        self._default_handlers = (
            list(default_handlers) 
            if default_handlers is not None 
            else [ConsoleHandler()]
        )
        self._loggers: dict[str, Logger] = {}

    def get_logger(
        self,
        name: str,
        *,
        level: LogLevel | None = None,
        handlers: Iterable[Handler] | None = None,
        filters: Iterable[Filter] | None = None,
    ) -> Logger:
        """
        Return a cached logger or create one if it doesn't exist.
        """
        logger = self._loggers.get(name)

        if logger is not None:
            return logger

        logger = Logger(
            name=name,
            level=level or self._default_level,
            handlers=(
                list(handlers)
                if handlers is not None
                else list(self._default_handlers)
            ),
            filters=filters,
            record_factory=self._record_factory
        )

        self._loggers[name] = logger
        return logger

    def clear(self) -> None:
            """
            Close all handlers and remove every cached logger.
            """

            for logger in self._loggers.values():
                logger.close()

            self._loggers.clear()