from __future__ import annotations
import threading
import os
import threading
from collections.abc import Mapping
from datetime import datetime, UTC
from typing import Any

from .caller_info import CallerInspector
from .exception_info import ExceptionInfo
from .levels import LogLevel
from .record import LogRecord
from .utils.immutable import freeze_mapping

class LogRecordFactory:
    """
    Responsible for construting immutable LogRecord instances.
    """

    __slots__ = ("_caller_inspector",)

    def __init__(self, caller_inspector: CallerInspector) -> None:
        self._caller_inspector = caller_inspector

    def create(
        self, 
        *, 
        level: LogLevel, 
        logger_name: str, 
        message: str, 
        exception: BaseException | None = None,
        extra: Mapping[str, Any] | None = None
    ):
        """
        Create an immutable log record
        """
        caller = self._caller_inspector.inspect()
        
        return LogRecord(
            timestamp=datetime.now(UTC),
            level=level,
            logger_name=logger_name,
            message=message,
            process_id=os.getpid(),
            thread_id=threading.get_ident(),
            caller=caller,
            exception=(
                ExceptionInfo.from_exception(exception) if exception is not None else None
            ),
            extra=freeze_mapping(extra)
        )