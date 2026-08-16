# pylog

A lightweight, modern, and extensible logging library for Python.

`pylog` is built from scratch with a focus on clean architecture, immutability, thread safety, structured logging, and extensibility. It provides a simple API while keeping the internal design modular and easy to extend.

> **Current Version:** v2.0

---

## Features

* Simple API with `get_logger()`
* Immutable log records
* Multiple log levels
* Console logging
* File logging
* Thread-safe handlers
* Asynchronous logging
* Rotating file logging
* Exception logging with tracebacks
* Structured logging with `extra`
* Context-aware logging
* JSON formatting
* Colored console output
* Multiple handlers per logger
* UTC timestamps
* Caller information
* Cached logger instances
* Extensible formatter architecture

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Shohaum/pylog.git

cd pylog
```

Install in editable mode:

```bash
pip install -e .
```

---

## Quick Start

```python
from pylog import get_logger

logger = get_logger("App")

logger.info("Application started")
logger.warning("Disk space is running low")
logger.error("Something went wrong")
```

Output:

```text
2026-08-16 15:40:18.848358 UTC [INFO] [App] Application started (/path/to/main.py:6)
```

---

## Log Levels

`pylog` provides six log levels:

```text
TRACE
DEBUG
INFO
WARNING
ERROR
CRITICAL
```

The default level is `INFO`.

```python
from pylog import get_logger
from pylog.levels import LogLevel

logger = get_logger(
    "App",
    level=LogLevel.DEBUG,
)

logger.debug("Debug information")
logger.info("Application started")
```

Messages below the configured level are ignored.

---

## Exception Logging

Exceptions are captured as immutable snapshots using Python's `TracebackException`.

```python
try:
    10 / 0
except Exception as exc:
    logger.exception(
        "Division failed",
        exception=exc,
    )
```

Output:

```text
2026-08-16 15:40:18.848358 UTC [ERROR] [App] Division failed (/path/to/main.py:12)

Traceback (most recent call last):
...
ZeroDivisionError: division by zero
```

---

## Structured Logging

Additional structured data can be attached to individual log records using `extra`.

```python
logger.info(
    "User logged in",
    extra={
        "user_id": 42,
        "country": "India",
    },
)
```

The metadata is stored as an immutable snapshot and can be consumed by different formatters.

---

## Logging Context

Context can be attached to all log records created within a scope.

```python
with logger.context(
    request_id="req-123",
    user_id=42,
):
    logger.info("Request started")
    logger.info("Fetching user")
    logger.info("Request completed")
```

The resulting records automatically contain:

```text
request_id=req-123
user_id=42
```

Contexts can also be nested:

```python
with logger.context(request_id="req-123"):
    logger.info("Request started")

    with logger.context(user_id=42):
        logger.info("User loaded")

    logger.info("Request completed")
```

Context is implemented using Python's `ContextVar`, allowing it to work correctly with concurrent execution contexts.

---

## File Logging

```python
from pylog import get_logger
from pylog.handlers import FileHandler

logger = get_logger("App")

logger.add_handler(
    FileHandler("logs/app.log")
)

logger.info("Written to file")
```

---

## Rotating File Logging

`RotatingFileHandler` automatically rotates the log file when it reaches a configured size.

```python
from pylog import get_logger
from pylog.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    "logs/app.log",
    max_bytes=1024 * 1024,
    backup_count=5,
)

logger = get_logger(
    "App",
    handlers=[handler],
)

logger.info("Application started")
```

This produces files such as:

```text
logs/
├── app.log
├── app.log.1
├── app.log.2
├── app.log.3
├── app.log.4
└── app.log.5
```

The newest rotated file is always `.1`.

---

## Asynchronous Logging

`AsyncHandler` moves formatting and output processing to a background worker thread.

```python
from pylog import get_logger
from pylog.handlers import AsyncHandler, FileHandler

handler = AsyncHandler(
    FileHandler("logs/app.log")
)

logger = get_logger(
    "App",
    handlers=[handler],
)

logger.info("This is processed asynchronously")

logger.close()
```

The application thread places the immutable `LogRecord` into a queue while the worker thread performs the actual handler processing.

`close()` performs a graceful shutdown and waits for queued records to be processed.

---

## JSON Logging

Use `JsonFormatter` when logs need to be consumed by log aggregation or monitoring systems.

```python
from pylog import get_logger
from pylog.formatter import JsonFormatter
from pylog.handlers import ConsoleHandler

logger = get_logger(
    "API",
    handlers=[
        ConsoleHandler(
            formatter=JsonFormatter()
        )
    ],
)

with logger.context(
    request_id="req-123",
    user_id=42,
):
    logger.info("Request started")
```

Example output:

```json
{
    "timestamp": "2026-08-16T15:40:18.848358+00:00",
    "level": "INFO",
    "logger": "API",
    "message": "Request started",
    "process_id": 12345,
    "thread_id": 123456,
    "extra": {
        "request_id": "req-123",
        "user_id": 42
    },
    "caller": {
        "file": "/path/to/main.py",
        "function": "<module>",
        "line": 12
    }
}
```

---

## Colored Console Output

`ColoredFormatter` provides ANSI-colored output based on the log level.

```python
from pylog import get_logger
from pylog.formatter import ColoredFormatter
from pylog.handlers import ConsoleHandler

logger = get_logger(
    "App",
    handlers=[
        ConsoleHandler(
            formatter=ColoredFormatter()
        )
    ],
)

logger.debug("Debug information")
logger.info("Application started")
logger.warning("Cache miss")
logger.error("Database timeout")
logger.critical("System failure")
```

> Currently, `ColoredFormatter` should be used with terminal output. Automatic TTY detection is planned for V3.

---

## Multiple Handlers

A logger can send the same record to multiple handlers.

```python
from pylog import get_logger
from pylog.formatter import JsonFormatter
from pylog.handlers import (
    ConsoleHandler,
    FileHandler,
)

logger = get_logger(
    "App",
    handlers=[
        ConsoleHandler(),
        FileHandler(
            "logs/app.log",
            formatter=JsonFormatter(),
        ),
    ],
)

logger.info("Application started")
```

Each handler can have its own formatter and output destination.

---

## Project Structure

```text
pylog/
│
├── __init__.py
├── _internal.py
├── caller_info.py
├── context.py
├── exception_info.py
├── formatter.py
├── handlers.py
├── levels.py
├── logger.py
├── manager.py
├── record.py
├── record_factory.py
└── utils/
    └── immutable.py
```

---

## Architecture

The core logging pipeline is:

```text
Application
     │
     ▼
   Logger
     │
     ▼
LogRecordFactory
     │
     ├── CallerInspector
     ├── ExceptionInfo
     ├── Logging Context
     └── Immutable Metadata
     │
     ▼
 LogRecord
     │
     ▼
  Handler
     │
     ├── ConsoleHandler
     ├── FileHandler
     ├── AsyncHandler
     └── RotatingFileHandler
     │
     ▼
 Formatter
     │
     ├── DefaultFormatter
     ├── JsonFormatter
     └── ColoredFormatter
```

The `LogRecord` is immutable and contains all information necessary for downstream processing.

---

## Design Principles

This project follows a few core principles:

* Single Responsibility Principle
* Immutable log records
* Separation of concerns
* Composition over inheritance
* Explicit dependencies
* Thread-safe handlers
* Structured data over formatted strings
* Minimal public API
* Extensible architecture
* Standard-library primitives where appropriate

---

## Roadmap

### V3

* Automatic TTY detection for `ColoredFormatter`
* Logging filters
* Handler-level filtering
* Logger hierarchy
* Improved configuration system
* Context propagation improvements
* Expanded test suite
* Performance benchmarks
* Packaging and PyPI readiness

### Future

* Time-based rotating files
* Log compression
* Remote logging
* OpenTelemetry integration
* Additional structured logging features

---

## License

MIT License
