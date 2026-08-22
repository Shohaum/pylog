"""
Defines log severity levels used throughout the logging system.

This module intentionally contains no formatting logic,
colors, or output-related behavior.
"""

from enum import IntEnum

class LogLevel(IntEnum):
    """
    Represents the severity of a log message.

    Higher values indicate higher severity.
    """

    TRACE = 5
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50