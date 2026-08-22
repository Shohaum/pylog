from __future__ import annotations
from collections.abc import Iterable

from .context import bind, clear_context, get_context
from .filters import (
    Filter,
    FunctionFilter,
    LevelFilter,
    LoggerNameFilter,
)
from .formatter import (
    ColoredFormatter,
    DefaultFormatter,
    Formatter,
    JsonFormatter,
)
from .handlers import (
    AsyncHandler,
    ConsoleHandler,
    FileHandler,
    Handler,
    RotatingFileHandler,
)
from .levels import LogLevel
from .logger import Logger
from .manager import LoggerManager

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
) -> Logger:
    """
    Return a cached logger for the given name.
    """
    return _manager.get_logger(
        name,
        level=level,
        handlers=handlers,
        filters=filters,
        propagate=propagate,
    )

def shutdown() -> None:
    """
    Gracefully shut down the global logging system.
    """
    _manager.clear()

__all__ = [
    # Core
    "Logger",
    "LoggerManager",
    "LogLevel",
    "get_logger",
    "configure",
    "shutdown",

    # Handlers
    "Handler",
    "ConsoleHandler",
    "FileHandler",
    "RotatingFileHandler",
    "AsyncHandler",

    # Formatters
    "Formatter",
    "DefaultFormatter",
    "JsonFormatter",
    "ColoredFormatter",

    # Filters
    "Filter",
    "LevelFilter",
    "LoggerNameFilter",
    "FunctionFilter",

    # Context
    "bind",
    "clear_context",
    "get_context",
]