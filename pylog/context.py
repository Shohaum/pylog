from __future__ import annotations
from collections.abc import Mapping
from contextlib import contextmanager
from contextvars import ContextVar, Token
from types import MappingProxyType
from typing import Any, Iterator

_EMPTY_CONTEXT: Mapping[str, Any] = MappingProxyType({})

_context: ContextVar[Mapping[str, Any]] = ContextVar(
    "pylog_context",
    default=_EMPTY_CONTEXT,
)

def get_context() -> Mapping[str, Any]:
    """
    Return an immutable snapshot of the current logging context.
    """
    return MappingProxyType(dict(_context.get()))

@contextmanager
def bind(
    values: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> Iterator[None]:
    """
    Temporarily add values to the current logging context.

    Nested contexts inherit values from their parent.

    Values supplied through ``kwargs`` override values supplied
    through ``values``.
    """

    current = _context.get()

    merged = dict(current)

    if values is not None:
        merged.update(values)

    merged.update(kwargs)

    token: Token[Mapping[str, Any]] = _context.set(
        MappingProxyType(merged)
    )

    try:
        yield
    finally:
        _context.reset(token)

@contextmanager
def clear_context() -> Iterator[None]:
    """
    Temporarily clear the current logging context.

    The previous context is restored when the context exits.
    """

    token = _context.set(_EMPTY_CONTEXT)

    try:
        yield
    finally:
        _context.reset(token)