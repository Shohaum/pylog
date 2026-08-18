from __future__ import annotations
from collections.abc import Iterable

from .filters import (
    Filter,
    FunctionFilter,
    LevelFilter,
    LoggerNameFilter,
)
from .handlers import Handler
from .levels import LogLevel
from .manager import LoggerManager
from .context import bind, clear_context, get_context

_manager = LoggerManager()

def configure(
    *,
    level: LogLevel | None = None,
    handlers: Iterable[Handler] | None = None,
) -> None:
    """
    Configure the global logging system.

    Configuration is applied to the root logger.
    Child loggers inherit the configuration unless they
    explicitly override it.
    """

    _manager.configure(
        level=level,
        handlers=handlers,
    )

def get_logger(
    name: str,
    *,
    level: LogLevel | None = None,
    handlers: Iterable[Handler] | None = None,
    filters: Iterable[Filter] | None = None,
    propagate: bool = True,
):
    return _manager.get_logger(
        name,
        level=level,
        handlers=handlers,
        filters=filters,
        propagate=propagate,
    )

def shutdown() -> None:
    """
    Gracefully shut down the logging system.
    """
    _manager.clear()


__all__ = [
    "Filter",
    "FunctionFilter",
    "LevelFilter",
    "LoggerNameFilter",
    "LogLevel",
    "configure",
    "get_logger",
    "shutdown",
    "bind",
    "clear_context",
    "get_context",
]