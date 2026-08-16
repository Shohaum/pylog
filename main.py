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
from pylog import get_logger
from pylog.handlers import AsyncHandler, FileHandler

handler = AsyncHandler(
    FileHandler("logs/async.log")
)

logger = get_logger(
    "AsyncTest",
    handlers=[handler],
)

for i in range(1000):
    logger.info(f"Message {i}")

logger.close()