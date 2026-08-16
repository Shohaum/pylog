from __future__ import annotations
from collections.abc import Iterable

from .handlers import Handler
from .levels import LogLevel
from .manager import LoggerManager

_manager = LoggerManager()

def get_logger(
    name: str,
    *,
    level: LogLevel | None = None,
    handlers: Iterable[Handler] | None = None,
):
    return _manager.get_logger(
        name,
        level=level,
        handlers=handlers,
    )