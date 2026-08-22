from __future__ import annotations
from dataclasses import dataclass
from traceback import TracebackException

@dataclass(frozen=True, slots=True)
class ExceptionInfo:
    """
    Immutable snapshot of an exception.

    Stores a TracebackException instead of a live traceback to avoid
    retaining stack frames and local variables.
    """
    traceback: TracebackException

    def __post_init__(self) -> None:
        if not isinstance(self.traceback, TracebackException):
            raise TypeError("traceback must be a TracebackException")

    @classmethod
    def from_exception(cls, exc: BaseException) -> "ExceptionInfo":
        if not isinstance(exc, BaseException):
            raise TypeError("exc must be a BaseException")
        return cls(traceback = TracebackException.from_exception(exc))
    
    @property
    def exception_type(self) -> str:
        """Name of the exception class"""
        return self.traceback.exc_type.__name__

    @property
    def message(self) -> str:
        """Exception message"""
        return "".join(self.traceback.format_exception_only()).strip()

    def format(self) -> str:
        """
        Return the formatted traceback

        This is imtentionally a thin wrapper around TracebackExcaption.format().
        """
        return "".join(self.traceback.format())