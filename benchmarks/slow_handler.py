from __future__ import annotations
import time

from xylog.handlers import Handler

class SlowHandler(Handler):
    """
    Simulates a slow logging destination.
    """

    __slots__ = ("_delay",)

    def __init__(self, delay: float = 0.001) -> None:
        super().__init__()
        self._delay = delay

    def write(self, message: str) -> None:
        time.sleep(self._delay)