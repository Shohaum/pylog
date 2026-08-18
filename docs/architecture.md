# pylog Architecture

> **A logging library should make the easy path simple without making
> the internal design simplistic.**

`pylog` is built around a small number of strict boundaries:

-   log events are immutable
-   record creation is isolated
-   formatting is separated from output
-   handlers own destinations
-   logger hierarchy controls propagation and inheritance
-   context is captured at record creation
-   asynchronous handlers decouple application code from slow I/O

The goal is not to reproduce every feature of Python's standard logging
package. It is to provide a small, understandable logging pipeline that
can evolve without collapsing its responsibilities into a single class.

# 1. The pipeline

``` text
Application
    │
    ▼
Logger
    │
    ├── effective level check
    ├── pre-record filters
    │
    ▼
LogRecordFactory
    │
    ├── timestamp
    ├── process/thread identity
    ├── caller information
    ├── context
    ├── exception snapshot
    └── immutable metadata
    │
    ▼
Immutable LogRecord
    │
    ├── filters
    │
    ▼
Handlers
    │
    ├── Formatter
    └── destination
```

The key boundary is:

``` text
Application
     │
     ▼
immutable LogRecord
     │
     ▼
logging pipeline
```

Once a record exists, the pipeline can process it without depending on
mutable application state.

# 2. LogRecord

`LogRecord` is the immutable representation of one logging event.

It contains the timestamp, level, logger name, message, process/thread
identity, caller information, exception information, and structured
metadata.

It knows nothing about formatting, handlers, files, queues, or
configuration.

> **A historical log event should not change after it has been
> created.**

The record is a frozen, slotted dataclass.

# 3. Immutability

Logging is historical data. If a dictionary changes after a log call,
the historical event must not silently change with it.

The ownership model is:

``` text
Application metadata
        │
        │ copy
        ▼
immutable snapshot
        │
        ▼
    LogRecord
```

This is especially important for asynchronous logging, where a record
may remain in a queue after the application has moved on.

# 4. LogRecordFactory

`LogRecordFactory` is the dedicated construction boundary.

The logger does not assemble timestamps, caller information, process
IDs, exception snapshots, or context metadata itself.

``` text
Logger
   │
   ▼
LogRecordFactory
   │
   ├── CallerInspector
   ├── Context
   ├── ExceptionInfo
   └── immutable metadata
   │
   ▼
LogRecord
```

This keeps record construction centralized and prevents `Logger` from
becoming a god object.

# 5. Caller inspection

`CallerInspector` isolates stack inspection.

It produces:

``` text
CallerInfo
├── file_path
├── function_name
└── line_number
```

The logger and formatters do not need to understand stack walking.

# 6. Exception handling

`ExceptionInfo` stores a `TracebackException` snapshot instead of
retaining a live traceback.

This avoids keeping stack frames and their local variables alive
unnecessarily.

``` text
BaseException
      │
      ▼
TracebackException
      │
      ▼
ExceptionInfo
      │
      ▼
immutable LogRecord
```

# 7. Logger

`Logger` is the application's primary interface.

Its responsibilities are:

-   expose logging methods
-   perform level checks
-   run filters
-   request record creation
-   send records to handlers
-   participate in hierarchy propagation
-   manage logger-local configuration

All convenience methods ultimately use the same `log()` pipeline.

# 8. Logger hierarchy

Logger names form a hierarchy:

``` text
myapp
├── api
│   ├── auth
│   └── payments
└── database
```

A child can inherit configuration from its parent.

Propagation allows a higher-level logger to own destinations while code
uses precise child names.

A logger can disable propagation when it needs independent output.

# 9. Global configuration

`LoggerManager` owns global configuration and the logger cache.

The public API remains small:

``` python
configure(
    level=LogLevel.INFO,
    handlers=[...],
)
```

Then:

``` python
logger = get_logger("myapp.api.auth")
```

The manager owns the root logger, record factory, hierarchy
construction, cache, and global configuration.

# 10. Filters

Filters can reject a complete record through:

``` python
filter(record) -> bool
```

Filters that can decide earlier may implement:

``` python
pre_filter(
    level=...,
    logger_name=...,
) -> bool
```

This creates a cheap rejection path without weakening the general filter
contract.

For example:

``` text
DEBUG
  │
  ▼
LevelFilter(ERROR)
  │
  └── reject
```

can happen before `LogRecord` construction.

# 11. Formatters

Formatters convert records into strings.

``` python
class Formatter(ABC):
    @abstractmethod
    def format(self, record: LogRecord) -> str:
        ...
```

The formatter owns representation, not destination.

``` text
LogRecord
    │
    ▼
Formatter
    │
    ▼
str
```

Current formatter families include human-readable, JSON, and colored
output.

# 12. Handlers

Handlers own output destinations.

Current handler types include:

``` text
ConsoleHandler
FileHandler
RotatingFileHandler
AsyncHandler
```

The core separation is:

``` text
Formatter → representation
Handler   → destination
```

A JSON formatter can therefore be paired with a console or file handler
without either component knowing the implementation details of the
other.

# 13. Thread safety

Handlers synchronize writes with a lock.

``` text
Record
  │
  ▼
format
  │
  ▼
lock
  │
  ▼
write
```

The lock belongs to the handler because the destination is the shared
resource that requires synchronization.

# 14. Asynchronous logging

`AsyncHandler` moves work; it does not change the meaning of a log
event.

The producer performs:

``` text
Logger
   │
   ▼
LogRecord
   │
   ▼
Queue
   │
   ▼
return
```

The worker performs:

``` text
Queue
   │
   ▼
Handler
   │
   ▼
Formatter
   │
   ▼
I/O
```

The queued object is the completed immutable `LogRecord`.

We do not queue mutable dictionaries, live exceptions, or a callback
that reconstructs the event later.

# 15. Context propagation

Logging context uses `ContextVar`.

``` python
with logger.context(
    request_id="req-123",
    user_id=42,
):
    logger.info("Request started")
```

Context is captured by `LogRecordFactory` at record creation time:

``` text
ContextVar
    │
    ▼
LogRecordFactory
    │
    ▼
immutable LogRecord
    │
    ▼
Async queue
```

The worker therefore does not need the originating request's context.

Explicit `extra` metadata takes precedence over context values with the
same key.

# 16. Immutability boundary

One of the most important architectural decisions is where mutability
ends.

``` text
Application state
       │
       ▼
Logger
       │
       ▼
Record creation
       │
       ║  IMMUTABILITY BOUNDARY
       ▼
Immutable LogRecord
       │
       ├── Formatter
       ├── Filter
       ├── Handler
       └── Async Queue
```

Everything after this boundary can safely share the same record.

# 17. Package responsibilities

``` text
pylog/
│
├── __init__.py          Public API
├── levels.py            Log severity definitions
├── record.py            Immutable event representation
├── record_factory.py    Record construction
├── caller_info.py       Caller inspection
├── exception_info.py    Exception snapshots
├── context.py           ContextVar-based metadata
├── filters.py           Record filtering
├── formatter.py         Record formatting
├── handlers.py          Output destinations
├── logger.py            Application logging interface
├── manager.py           Logger hierarchy and global management
│
└── utils/
    └── immutable.py     Immutable data helpers
```

Each module should have a clear reason to change.

# 18. Dependency direction

``` text
                    ┌─────────────┐
                    │   Logger    │
                    └──────┬──────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ LogRecordFactory│
                  └────────┬────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  LogRecord  │
                    └──────┬──────┘
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
          Filters      Formatters     Handlers
                                         │
                              ┌──────────┼──────────┐
                              ▼          ▼          ▼
                           Console     File       Async
```

`LogRecord` remains a data object rather than becoming aware of the
machinery around it.

# 19. Design principles

## Single Responsibility

Each component should have one primary reason to change.

## Immutability

A log event becomes immutable at record creation.

## Separation of concerns

Creation, filtering, formatting, and output are separate stages.

## Composition over inheritance

Handlers and formatters should be composable without large inheritance
trees.

## Performance through architecture

The cheapest optimization is often avoiding unnecessary work. Pre-record
filtering is more valuable than making unnecessary record construction
5% faster.

## Extensibility without speculation

New abstractions should solve demonstrated requirements rather than
anticipate every possible future feature.

# 20. Contributing to the architecture

Before introducing an abstraction, ask:

1.  What responsibility does it own?
2.  What responsibility should it explicitly not own?
3.  Does it preserve the immutable `LogRecord` boundary?
4.  Does it introduce unnecessary shared mutable state?
5.  Can the behavior be tested independently?
6.  Can a benchmark demonstrate a claimed performance benefit?
7.  Does it make the system easier or harder to reason about?

A good contribution should improve the library without making its core
pipeline mysterious.

# 21. Current architecture

At V3, the core pipeline is:

``` text
Application
    │
    ▼
Logger
    │
    ├── level check
    ├── pre-record filters
    │
    ▼
LogRecordFactory
    │
    ├── caller
    ├── timestamp
    ├── context
    ├── exception snapshot
    └── immutable metadata
    │
    ▼
Immutable LogRecord
    │
    ├── filters
    │
    ▼
Handlers
    │
    ├── Console
    ├── File
    ├── Rotating File
    └── Async
            │
            ▼
        background worker
```

# 22. Future direction

Potential areas include richer structured logging, sampling,
backpressure policies, configurable async queues, compression, remote
handlers, OpenTelemetry integration, high-concurrency profiling, and
richer configuration.

Future features should preserve the core principle:

> **Keep the logging event simple, immutable, and independent from the
> machinery that transports it.**