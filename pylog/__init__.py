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


_manager = LoggerManager()


def get_logger(
    name: str,
    *,
    level: LogLevel | None = None,
    handlers: Iterable[Handler] | None = None,
    filters: Iterable[Filter] | None = None,
    propagate: bool = True
):
    return _manager.get_logger(
        name,
        level=level,
        handlers=handlers,
        filters=filters,
        propagate=propagate
    )


__all__ = [
    "Filter",
    "FunctionFilter",
    "LevelFilter",
    "LoggerNameFilter",
    "LogLevel",
    "get_logger",
]