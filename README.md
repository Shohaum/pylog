# pylog

A lightweight, modern, and extensible logging library for Python.

`pylog` is built from scratch with a focus on clean architecture, immutable log records, thread safety, structured logging, asynchronous processing, and extensibility.

> **Current Version:** v3.0.0

---

## Features

- Simple API with `get_logger()`
- Global logging configuration
- Logger hierarchy and propagation
- Immutable log records
- Six log levels
- Console logging
- File logging
- Rotating file logging
- Asynchronous logging
- Thread-safe handlers
- Exception logging with immutable traceback snapshots
- Structured logging with `extra`
- Context-aware logging using `ContextVar`
- JSON formatting
- Colored console output
- Automatic TTY-aware colored output
- Multiple handlers per logger
- Multiple formatters
- Custom filters
- Pre-record filtering for inexpensive rejection
- UTC timestamps
- Caller information
- Cached logger instances
- Graceful shutdown
- Extensible formatter and handler architecture
- Performance benchmarks

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Shohaum/pylog.git
cd pylog
```

Install in editable mode:

```bash
python -m pip install -e .
```

For development:

```bash
python -m pip install -e ".[dev]"
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

Example output:

```text
2026-08-22 11:20:18.848358 UTC [INFO] [App] Application started (/path/to/main.py:6)
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

Messages below the configured effective level are ignored.

---

## Global Configuration

Applications can configure the logging system once and allow child loggers to inherit the configuration.

```python
from pylog import configure, get_logger
from pylog.handlers import ConsoleHandler, FileHandler
from pylog.levels import LogLevel

configure(
    level=LogLevel.INFO,
    handlers=[
        ConsoleHandler(),
        FileHandler("logs/app.log"),
    ],
)

logger = get_logger("App.API")

logger.info("Request started")
```

Individual loggers can still override the inherited level, handlers, filters, or propagation behavior.

---

## Logger Hierarchy

Logger names form a hierarchy using `.` as the separator.

```python
from pylog import get_logger

app = get_logger("app")
api = get_logger("app.api")
auth = get_logger("app.api.auth")
```

The resulting hierarchy is:

```text
app
├── api
│   └── auth
```

Child loggers inherit configuration from their parents unless explicitly overridden.

By default, records propagate toward the root logger.

```python
logger = get_logger(
    "app.api.auth",
    propagate=False,
)
```

This disables propagation for that logger.

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

Example output:

```text
2026-08-22 11:20:18.848358 UTC [ERROR] [App] Division failed (/path/to/main.py:12)
Traceback (most recent call last):
...
ZeroDivisionError: division by zero
```

The logging system does not retain live traceback frames and their local variables.

---

## Structured Logging

Additional structured data can be attached to individual records using `extra`.

```python
logger.info(
    "User logged in",
    extra={
        "user_id": 42,
        "country": "India",
    },
)
```

The metadata is captured as an immutable snapshot when the `LogRecord` is created.

---

## Logging Context

Context can be attached to all records created within a scope.

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
request_id='req-123' user_id=42
```

Contexts can be nested:

```python
with logger.context(request_id="req-123"):
    logger.info("Request started")

    with logger.context(user_id=42):
        logger.info("User loaded")

    logger.info("Request completed")
```

The inner context inherits the outer context.

Context is implemented using Python's `ContextVar`, making it suitable for concurrent execution contexts.

The context is captured when the `LogRecord` is created, so asynchronous handlers do not depend on the context of the originating thread.

You can also use the context API directly:

```python
from pylog import bind, clear_context, get_context

with bind(request_id="req-123"):
    ...
```

---

## File Logging

```python
from pylog import get_logger
from pylog.handlers import FileHandler

logger = get_logger(
    "App",
    handlers=[
        FileHandler("logs/app.log"),
    ],
)

logger.info("Written to file")
```

`FileHandler` creates the parent directory when necessary and flushes each record after writing.

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

`AsyncHandler` processes another handler in a background worker thread.

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

logger.info("Processed asynchronously")

logger.close()
```

The application thread creates the immutable `LogRecord` and places it into a queue. The worker thread performs formatting and output processing.

`close()` performs a graceful shutdown and waits for queued records to be processed.

### Why asynchronous logging?

Async logging is particularly useful when the logging destination is slow.

The application path becomes:

```text
Application thread
      │
      ▼
LogRecord
      │
      ▼
Queue
      │
      └──────────────► return
                       │
                       ▼
                 Worker thread
                       │
                       ▼
                  Format + I/O
```

The I/O work is not eliminated; it is moved away from the application thread.

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
            formatter=JsonFormatter(),
        ),
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
  "timestamp": "2026-08-22T11:20:18.848358+00:00",
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

`ColoredFormatter` provides ANSI-colored output based on log level.

```python
from pylog import get_logger
from pylog.formatter import ColoredFormatter
from pylog.handlers import ConsoleHandler

logger = get_logger(
    "App",
    handlers=[
        ConsoleHandler(
            formatter=ColoredFormatter(),
        ),
    ],
)

logger.debug("Debug information")
logger.info("Application started")
logger.warning("Cache miss")
logger.error("Database timeout")
logger.critical("System failure")
```

`ColoredFormatter` automatically detects whether the output stream is a TTY and only emits ANSI color codes when appropriate.

---

## Multiple Handlers

A logger can send the same record to multiple handlers.

```python
from pylog import get_logger
from pylog.formatter import JsonFormatter
from pylog.handlers import ConsoleHandler, FileHandler

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

## Filters

Filters can determine whether a record should be emitted.

```python
from pylog import get_logger
from pylog.filters import LevelFilter
from pylog.levels import LogLevel

logger = get_logger(
    "App",
    filters=[
        LevelFilter(LogLevel.WARNING),
    ],
)

logger.info("Ignored")
logger.warning("Allowed")
logger.error("Allowed")
```

`pylog` includes:

- `Filter`
- `LevelFilter`
- `LoggerNameFilter`
- `FunctionFilter`

Filters that can make a decision from inexpensive information can reject a message before `LogRecord` construction.

This avoids unnecessary caller inspection, context capture, and record creation.

---

## Handlers

The built-in handlers are:

```text
Handler
├── ConsoleHandler
├── FileHandler
├── RotatingFileHandler
└── AsyncHandler
```

Handlers are thread-safe and responsible for output processing.

Custom handlers can be created by subclassing `Handler` and implementing `write()`.

---

## Formatters

The built-in formatters are:

```text
Formatter
├── DefaultFormatter
├── JsonFormatter
└── ColoredFormatter
```

Formatters are responsible only for converting a `LogRecord` into its output representation.

Custom formatters can be created by implementing:

```python
from pylog.formatter import Formatter

class MyFormatter(Formatter):
    def format(self, record):
        return record.message
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
     ├── Level check
     ├── Pre-record filters
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
   Filters
     │
     ▼
  Handlers
     │
     ├── ConsoleHandler
     ├── FileHandler
     ├── RotatingFileHandler
     └── AsyncHandler
     │
     ▼
 Formatters
     │
     ├── DefaultFormatter
     ├── JsonFormatter
     └── ColoredFormatter
     │
     ▼
   Destination
```

The `LogRecord` is immutable and contains the historical information needed by downstream processing.

The asynchronous handler preserves this property by queuing the already-created record rather than reconstructing logging context later.

---

## Design Principles

The project follows these principles:

- Single Responsibility Principle
- Immutable log records
- Separation of concerns
- Composition over inheritance
- Explicit dependencies
- Thread-safe handlers
- Structured data over formatted strings
- Cheap rejection before expensive work
- Minimal public API
- Extensible architecture
- Standard-library primitives where appropriate
- Measure before optimizing

---

## Performance

Performance is measured using a dedicated benchmark suite with 10,000 iterations.

Baseline results on the development machine:

| Operation | Per operation |
|---|---:|
| Record creation | 27.28 µs |
| Filtered DEBUG | 0.25 µs |
| JSON formatting | 2.23 µs |
| File logging | 51.50 µs |
| Async logging | 67.74 µs |
| Context logging | 48.51 µs |

### Pre-record filtering

Before optimization, rejected DEBUG messages took approximately `47.42 µs/op`.

After adding pre-record filtering:

```text
47.42 µs/op → 0.25 µs/op
```

This represents approximately **99.47% lower latency** for that rejection path.

### Asynchronous logging

A benchmark using a deliberately slow handler demonstrated the intended purpose of `AsyncHandler`.

With a 1 ms delay per write:

| Metric | Synchronous | Asynchronous |
|---|---:|---:|
| Application time | 1.5964 s | 0.0845 s |
| Per operation | 1596.38 µs | 84.46 µs |

This reduced application-thread logging time by approximately **94.7%**.

The underlying I/O work still occurs; asynchronous logging moves it to the worker thread.

See [`benchmark.md`](benchmark.md) for methodology and optimization history.

---

## Project Structure

```text
pylog/
│
├── pylog/
│   ├── __init__.py
│   ├── _internal.py
│   ├── caller_info.py
│   ├── context.py
│   ├── exception_info.py
│   ├── filters.py
│   ├── formatter.py
│   ├── handlers.py
│   ├── levels.py
│   ├── logger.py
│   ├── manager.py
│   ├── record.py
│   ├── record_factory.py
│   └── utils/
│       └── immutable.py
│
├── benchmarks/
│   ├── benchmarks.py
│   └── slow_handler.py
│
├── tests/
│
├── docs/
│   ├── benchmarks.md
│   └── architecture.md
├── README.md
├── pyproject.toml
└── .gitignore
```

---

## Development

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project with development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Run the test suite:

```bash
pytest
```

Run the benchmarks:

```bash
python3 -m benchmarks.benchmarks
```

---

## Public API

The primary API is intentionally small:

```python
from pylog import (
    configure,
    get_logger,
    shutdown,
)
```

Advanced functionality is available through handlers, formatters, filters, and context utilities.

```python
from pylog import (
    AsyncHandler,
    ColoredFormatter,
    FileHandler,
    LevelFilter,
    RotatingFileHandler,
)
```

---

## Versioning

The project follows semantic versioning.

Current release:

```text
3.0.0
```

---

## Future

Potential future features include:

- Time-based rotating files
- Log compression
- Remote logging
- OpenTelemetry integration
- Additional structured logging features
- More advanced configuration
- Metrics and observability integrations

---

## License

MIT License