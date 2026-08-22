from __future__ import annotations
import inspect
from dataclasses import dataclass
from pathlib import Path

from ._internal import LIBRARY_ROOT


@dataclass(frozen=True, slots=True)
class CallerInfo:
    file_path: str
    function_name: str
    line_number: int

    def __post_init__(self) -> None:
        if not self.file_path:
            raise ValueError("file_path cannot be empty")

        if not self.function_name:
            raise ValueError("function_name cannot be empty")

        if self.line_number <= 0:
            raise ValueError("line_number must be greater than zero")


class CallerInspector:
    """
    Determines the application frame that initiated logging.
    """

    __slots__ = ("_library_root",)

    def __init__(self) -> None:
        self._library_root = LIBRARY_ROOT

    def inspect(self) -> CallerInfo:
        frame = inspect.currentframe()

        if frame is None:
            raise RuntimeError("Unable to inspect stack.")

        try:
            frame = frame.f_back

            while frame is not None:
                filename = Path(frame.f_code.co_filename).resolve()

                if not filename.is_relative_to(self._library_root):
                    return CallerInfo(
                        file_path=str(filename),
                        function_name=frame.f_code.co_name,
                        line_number=frame.f_lineno,
                    )

                frame = frame.f_back

        finally:
            del frame

        raise RuntimeError("Unable to determine caller.")