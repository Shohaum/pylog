from __future__ import annotations
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any

_context: ContextVar[dict[str, Any]] = ContextVar(
    "pylog_context",
    default={},
)

def get_context() -> dict[str, Any]:
    """
    Return a copy of the current logging context.
    """
    return dict(_context.get())

@contextmanager
def bind(**values: Any):
    """
    Temporarily add values to the current logging context.

    Context values are automatically restored when the context exits.
    """
    current = _context.get()

    merged = current.copy()
    merged.update(values)

    token = _context.set(merged)

    try:
        yield
    finally:
        _context.reset(token)