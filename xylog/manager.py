from __future__ import annotations
from collections.abc import Iterable

from .caller_info import CallerInspector
from .filters import Filter
from .handlers import ConsoleHandler, Handler
from .levels import LogLevel
from .logger import Logger
from .record_factory import LogRecordFactory

class LoggerManager:
    """
    Creates and manages the logger hierarchy and global configuration.
    """

    __slots__ = (
        "_record_factory",
        "_loggers",
        "_root",
    )

    def __init__(
        self,
        *,
        default_level: LogLevel = LogLevel.INFO,
        default_handlers: Iterable[Handler] | None = None,
    ) -> None:
        inspector = CallerInspector()

        self._record_factory = LogRecordFactory(inspector)

        handlers = (
            list(default_handlers)
            if default_handlers is not None
            else [ConsoleHandler()]
        )

        self._root = Logger(
            name="",
            record_factory=self._record_factory,
            level=default_level,
            handlers=handlers,
            propagate=False,
        )

        self._loggers: dict[str, Logger] = {}

    @property
    def root(self) -> Logger:
        return self._root

    def configure(
        self,
        *,
        level: LogLevel | None = None,
        handlers: Iterable[Handler] | None = None,
    ) -> None:
        """
        Configure the root logger.

        Configuration applies to loggers that inherit their
        level and handlers through the hierarchy.
        """

        if level is not None:
            self._root.level = level

        if handlers is not None:
            self._replace_root_handlers(handlers)

    def _replace_root_handlers(
        self,
        handlers: Iterable[Handler],
    ) -> None:
        new_handlers = list(handlers)

        old_handlers = self._root.handlers

        self._root.set_handlers(new_handlers)

        for handler in old_handlers:
            handler.close()

    def get_logger(
        self,
        name: str,
        *,
        level: LogLevel | None = None,
        handlers: Iterable[Handler] | None = None,
        filters: Iterable[Filter] | None = None,
        propagate: bool = True,
    ) -> Logger:
        """
        Return a cached logger or create one if it doesn't exist.
        """

        if not name:
            return self._root

        logger = self._loggers.get(name)

        if logger is not None:
            return logger

        parent = self._find_parent(name)

        logger = Logger(
            name=name,
            record_factory=self._record_factory,
            level=level,
            handlers=(
                list(handlers)
                if handlers is not None
                else []
            ),
            filters=filters,
            parent=parent,
            propagate=propagate,
        )

        self._loggers[name] = logger

        self._reparent_children(logger)

        return logger

    def _find_parent(self, name: str) -> Logger:
        parts = name.split(".")

        for index in range(len(parts) - 1, 0, -1):
            parent_name = ".".join(parts[:index])

            parent = self._loggers.get(parent_name)

            if parent is not None:
                return parent

        return self._root

    def _reparent_children(self, logger: Logger) -> None:
        for child in self._loggers.values():
            if child is logger:
                continue

            if not child.name.startswith(
                f"{logger.name}."
            ):
                continue

            parent = self._find_parent(child.name)

            if parent is logger:
                child.set_parent(logger)

    def clear(self) -> None:
        """
        Close all loggers and reset the manager.
        """

        for logger in self._loggers.values():
            logger.close()

        self._root.close()

        self._loggers.clear()