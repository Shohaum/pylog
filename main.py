# Logger interface
# from pylog import get_logger

# logger = get_logger("Demo")

# logger.info("Application started")

# logger.debug("Debug message")

# logger.warning("Low disk space")

# logger.error("Something went wrong")

# Exception Catching
# try:
#     10 / 0
# except Exception as exc:
#     logger.exception(
#         "Division failed",
#         exception=exc,
#     )

# Logger Cache
# from pylog import get_logger

# logger1 = get_logger("Auth")
# logger2 = get_logger("Auth")

# print(logger1 is logger2)

# Different Loggers
# logger1 = get_logger("Auth")
# logger2 = get_logger("Database")

# print(logger1 is logger2)

# Log Level Filtering
# from pylog import get_logger
# from pylog.levels import LogLevel

# logger = get_logger("Demo")

# logger.level = LogLevel.ERROR

# logger.info("Hidden")

# logger.warning("Hidden")

# logger.error("Visible")

# File Handler
# from pylog import get_logger
# from pylog.handlers import FileHandler

# logger = get_logger("FileLogger")

# logger.add_handler(
#     FileHandler("logs/app.log")
# )

# logger.info("Written to file")

# # Extra Metadata
# logger.info(
#     "User logged in",
#     extra={
#         "user_id": 42,
#         "country": "India",
#     },
# )

# Thread Safety
# import threading

# from pylog import get_logger

# logger = get_logger("Threads")


# def worker(index: int):
#     for i in range(100):
#         logger.info(f"Worker {index}: {i}")


# threads = [
#     threading.Thread(target=worker, args=(i,))
#     for i in range(10)
# ]

# for t in threads:
#     t.start()

# for t in threads:
#     t.join()

# Multiple Handlers
# from pylog import get_logger
# from pylog.handlers import FileHandler

# logger = get_logger("Demo")

# logger.add_handler(
#     FileHandler("logs/demo.log")
# )

# logger.info("Hello")

# Json logging
# from pylog import get_logger
# from pylog.formatter import JsonFormatter
# from pylog.handlers import ConsoleHandler

# logger = get_logger(
#     "API",
#     handlers=[
#         ConsoleHandler(
#             formatter=JsonFormatter()
#         )
#     ],
# )

# with logger.context(
#     request_id="req-123",
#     user_id=42,
# ):
#     logger.info("Request started")

# Async logging
# from pylog import get_logger
# from pylog.handlers import AsyncHandler, FileHandler

# handler = AsyncHandler(
#     FileHandler("logs/async.log")
# )

# logger = get_logger(
#     "AsyncTest",
#     handlers=[handler],
# )

# for i in range(1000):
#     logger.info(f"Message {i}")

# logger.close()

# Rotating file handling
# from pylog import get_logger
# from pylog.handlers import RotatingFileHandler

# handler = RotatingFileHandler(
#     "logs/rotation.log",
#     max_bytes=500,
#     backup_count=3,
# )

# logger = get_logger(
#     "RotationTest",
#     handlers=[handler],
# )

# for i in range(100):
#     logger.info(
#         f"This is test message number {i}"
#     )

# logger.close()

# Color output in the terminal
# from pylog import get_logger
# from pylog.formatter import ColoredFormatter
# from pylog.handlers import ConsoleHandler

# logger = get_logger(
#     "API",
#     handlers=[
#         ConsoleHandler(
#             formatter=ColoredFormatter()
#         )
#     ],
# )

# logger.debug("Debug information")
# logger.info("Server started")
# logger.warning("Cache miss")
# logger.error("Database timeout")
# logger.critical("System failure")

# Integration testing
# from pylog import get_logger
# from pylog.formatter import JsonFormatter
# from pylog.handlers import AsyncHandler, RotatingFileHandler

# handler = AsyncHandler(
#     RotatingFileHandler(
#         "logs/integration.log",
#         max_bytes=5_000,
#         backup_count=3,
#         formatter=JsonFormatter(),
#     )
# )

# logger = get_logger(
#     "IntegrationTest",
#     handlers=[handler],
# )

# with logger.context(
#     request_id="req-123",
#     user_id=42,
# ):
#     for i in range(1_000):
#         logger.info(
#             "Processing request",
#             extra={"iteration": i},
#         )

# logger.close()

# TTY test
# from pylog import get_logger
# from pylog.formatter import ColoredFormatter
# from pylog.handlers import ConsoleHandler

# logger = get_logger(
#     "TTYTest",
#     handlers=[
#         ConsoleHandler(
#             formatter=ColoredFormatter()
#         )
#     ],
# )

# logger.debug("Debug message")
# logger.info("Info message")
# logger.warning("Warning message")
# logger.error("Error message")
# logger.critical("Critical message")

# Color formatter with file handler
# from pylog import get_logger
# from pylog.formatter import ColoredFormatter
# from pylog.handlers import FileHandler

# logger = get_logger(
#     "FileTest",
#     handlers=[
#         FileHandler(
#             "logs/color_test.log",
#             formatter=ColoredFormatter(),
#         )
#     ],
# )

# logger.info("This should not contain ANSI colors")

# logger.close()

# TTY detection with async handler
# from pylog import get_logger
# from pylog.formatter import ColoredFormatter
# from pylog.handlers import AsyncHandler, ConsoleHandler

# logger = get_logger(
#     "AsyncTTY",
#     handlers=[
#         AsyncHandler(
#             ConsoleHandler(
#                 formatter=ColoredFormatter()
#             )
#         )
#     ],
# )

# for i in range(100):
#     logger.info(f"Message {i}")

# logger.close()

# Logger filter
# from pylog import get_logger
# from pylog.filters import LevelFilter
# from pylog.levels import LogLevel

# logger = get_logger(
#     "FilterTest",
#     level=LogLevel.DEBUG,
#     filters=[
#         LevelFilter(LogLevel.ERROR),
#     ],
# )

# logger.debug("Should NOT appear")
# logger.info("Should NOT appear")
# logger.warning("Should NOT appear")
# logger.error("Should appear")
# logger.critical("Should appear")

# logger.close()

# Logger filter with different handlers
# from pylog import get_logger
# from pylog.filters import LevelFilter
# from pylog.handlers import ConsoleHandler, FileHandler
# from pylog.levels import LogLevel

# console = ConsoleHandler()

# file_handler = FileHandler(
#     "logs/errors.log",
#     filters=[
#         LevelFilter(LogLevel.ERROR),
#     ],
# )

# logger = get_logger(
#     "HandlerFilterTest",
#     handlers=[
#         console,
#         file_handler,
#     ],
# )

# logger.info("Info message")
# logger.warning("Warning message")
# logger.error("Error message")

# logger.close()

# Logger filter with async
# from pylog import get_logger
# from pylog.filters import LevelFilter
# from pylog.handlers import AsyncHandler, FileHandler
# from pylog.levels import LogLevel

# handler = AsyncHandler(
#     FileHandler(
#         "logs/async-errors.log",
#     ),
#     filters=[
#         LevelFilter(LogLevel.ERROR),
#     ],
# )

# logger = get_logger(
#     "AsyncFilter",
#     handlers=[handler],
# )

# for i in range(100):
#     logger.info(f"Info {i}")

# for i in range(100):
#     logger.error(f"Error {i}")

# logger.close()

# Basic hierarchy
# from pylog import get_logger
# from pylog.levels import LogLevel

# app = get_logger("app")
# api = get_logger("app.api")
# auth = get_logger("app.api.auth")

# assert api.parent is app
# assert auth.parent is api

# print("Basic hierarchy passed")

# Level inheritence
# from pylog import get_logger
# from pylog.levels import LogLevel

# app = get_logger("app")
# api = get_logger("app.api")
# auth = get_logger("app.api.auth")
# app.level = LogLevel.WARNING

# assert api.level is None
# assert api.effective_level == LogLevel.WARNING

# assert auth.level is None
# assert auth.effective_level == LogLevel.WARNING

# print("Level inheritance passed")

# Child override
# from pylog import get_logger
# from pylog.levels import LogLevel

# app = get_logger("app")
# api = get_logger("app.api")
# auth = get_logger("app.api.auth")

# app.level = LogLevel.WARNING
# auth.level = LogLevel.DEBUG

# assert auth.effective_level == LogLevel.DEBUG
# assert api.effective_level == LogLevel.WARNING

# print("Child level override passed")

# Propagation test
# from pathlib import Path

# from pylog import get_logger
# from pylog.handlers import FileHandler

# log_path = Path("logs/hierarchy.log")

# if log_path.exists():
#     log_path.unlink()

# app = get_logger(
#     "application",
#     handlers=[
#         FileHandler(log_path)
#     ],
# )

# auth = get_logger("application.api.auth")

# auth.error("Authentication failed")

# app.close()
# auth.close()

# content = log_path.read_text()

# assert "Authentication failed" in content

# print("Propagation passed")

# Propagation disabled
# from pathlib import Path

# from pylog import get_logger
# from pylog.handlers import FileHandler

# log_path = Path("logs/no_propagation.log")

# if log_path.exists():
#     log_path.unlink()

# app = get_logger(
#     "service",
#     handlers=[
#         FileHandler(log_path)
#     ],
# )

# worker = get_logger(
#     "service.worker",
#     propagate=False,
# )

# worker.error("Worker failure")

# app.close()
# worker.close()

# content = (
#     log_path.read_text()
#     if log_path.exists()
#     else ""
# )

# assert "Worker failure" not in content

# print("Propagation disabled passed")

# Parent created AFTER child
# from pylog import get_logger

# child = get_logger("backend.api.auth")

# assert child.parent.name == ""

# parent = get_logger("backend.api")

# assert child.parent is parent

# print("Late parent creation passed")

# No duplicate logging
# from pylog import get_logger
# from pylog.handlers import FileHandler

# root = get_logger(
#     "myapp",
#     handlers=[
#         FileHandler("logs/duplicate.log")
#     ],
# )

# child = get_logger("myapp.api")

# child.error("ONE MESSAGE")

# root.close()
# child.close()

# Full hierarchy
from pylog import get_logger

root = get_logger("myapp")
api = get_logger("myapp.api")
auth = get_logger("myapp.api.auth")
payments = get_logger("myapp.api.payments")
worker = get_logger("myapp.worker")

assert api.parent is root
assert auth.parent is api
assert payments.parent is api
assert worker.parent is root

print("Full hierarchy passed")