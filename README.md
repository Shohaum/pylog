# pylog

A lightweight, modern, and extensible logging library for Python.

`pylog` is built from scratch with a focus on clean architecture, immutability, thread safety, and extensibility. It provides a simple API while keeping the internal design modular and easy to extend.

> **Current Version:** v1.0

---

## Features

- Simple API (`get_logger()`)
- Immutable log records
- Multiple log levels
- Console logging
- File logging
- Thread-safe handlers
- Exception logging with tracebacks
- Multiple handlers per logger
- UTC timestamps
- Extensible formatter architecture
- Cached logger instances

---

## Installation

Clone the repository:

```bash
git clone https://github.com/<your-username>/pylog.git

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
2026-07-26 18:25:10 UTC [INFO] [App] Application started
```

---

## Exception Logging

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
[ERROR] Division failed

Traceback (most recent call last):
...
ZeroDivisionError: division by zero
```

---

## File Logging

```python
from pylog.handlers import FileHandler

logger = get_logger("App")

logger.add_handler(
    FileHandler("logs/app.log")
)

logger.info("Written to file")
```

---

## Project Structure

```
pylog/
│
├── caller_info.py
├── exception_info.py
├── formatter.py
├── handlers.py
├── levels.py
├── logger.py
├── manager.py
├── record.py
├── record_factory.py
└── utils/
```

---

## Design Principles

This project follows a few simple principles:

- Single Responsibility Principle
- Immutable log records
- Separation of concerns
- Composition over inheritance
- Extensible architecture
- Minimal public API

---

### V2

- Async logging
- JSON formatter
- Rotating file handler
- Global configuration
- Custom formatter support
- Performance improvements

### Futures to add

- Structured logging
- Context-aware logging
- Colored console output
- Log filtering
- Compression
- Remote logging
- OpenTelemetry integration

---

## License

MIT License