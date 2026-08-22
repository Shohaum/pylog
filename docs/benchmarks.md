# xylog Performance Benchmarks

> **Performance is a feature. Measurement is part of the design.**

This document records the performance characteristics of `xylog` as the
library evolves. The goal is not to chase arbitrary microbenchmark
numbers, but to understand where time is spent, validate architectural
decisions, and make performance changes measurable and reproducible.

## Environment

  Property               Value
  ---------------------- ---------
  Python                 3.13.14
  OS                     macOS
  Architecture           arm64
  xylog version          v3.0
  Benchmark iterations   10,000

Numbers are machine-dependent. Their primary purpose is comparison on
the same environment.

## Methodology

Benchmarks use Python's `timeit` module with 10,000 iterations unless
otherwise specified.

``` text
Hypothesis
    ↓
Measure baseline
    ↓
Implement one change
    ↓
Run tests
    ↓
Measure again
    ↓
Compare
    ↓
Keep or revert
```

An optimization is accepted only when it preserves correctness and
demonstrates a meaningful improvement.

# Baseline

  Operation             Total   Per operation
  ----------------- --------- ---------------
  Record creation     0.2730s        27.30 µs
  Filtered DEBUG      0.4742s        47.42 µs
  JSON formatting     0.0217s         2.17 µs
  File logging        0.5268s        52.68 µs
  Async logging       0.6271s        62.71 µs
  Context logging     0.4863s        48.63 µs

### Record creation --- 27.30 µs/op

Includes caller inspection, timestamp creation, process/thread identity,
context capture, metadata merging, immutable metadata creation, and
`LogRecord` validation.

### Filtered DEBUG --- 47.42 µs/op

The original pipeline created a complete `LogRecord` before a
`LevelFilter` could reject it. This made filtered logging the first
optimization target.

### JSON formatting --- 2.17 µs/op

JSON serialization was inexpensive compared with record creation and
file I/O.

### File logging --- 52.68 µs/op

Includes record creation, formatting, handler locking, file writing, and
flushing.

### Async logging --- 62.71 µs/op

The initial benchmark measured submission latency. This should not be
interpreted as "async is slower": the purpose of async logging is to
decouple application execution from slow destinations.

### Context logging --- 48.63 µs/op

Includes context management, `ContextVar` operations, and record
creation.

# Optimization 1 --- Pre-record filtering

## Problem

Some filters can decide whether to accept a message without a complete
`LogRecord`.

Creating the record first was unnecessary work.

## Change

`Filter` gained an optional `pre_filter()` stage.

``` text
log call
   ↓
effective level
   ↓
pre_filter()
   ↓
reject? ── yes ──→ return
   │
   no
   ↓
LogRecordFactory
   ↓
LogRecord
   ↓
filter(record)
```

  Filter               Pre-record decision?   Reason
  -------------------- ---------------------- -----------------------------------
  `LevelFilter`        Yes                    Needs only log level
  `LoggerNameFilter`   Yes                    Needs only logger name
  `FunctionFilter`     No                     Needs caller information
  Custom filter        No by default          May require arbitrary record data

## Result

  Operation            Before     After         Improvement
  ---------------- ---------- --------- -------------------
  Filtered DEBUG     47.42 µs   0.25 µs   **99.47% faster**

The rejected message now avoids caller inspection, timestamp creation,
context capture, metadata copying, immutable mapping creation, and
record construction.

All tests passed.

# Async Logging Validation

## Question

Does `AsyncHandler` reduce application-thread latency when the logging
destination is slow?

A local file benchmark alone cannot answer this reliably, so a
deliberately slow handler was used. It sleeps for 1 ms per write and
1,000 messages were logged.

## Result

  Metric               Synchronous   Asynchronous
  ------------------ ------------- --------------
  Application time        1.5964 s       0.0845 s
  Per operation         1596.38 µs       84.46 µs
  Completion wait              ---       1.2021 s

Application-thread logging time was reduced by approximately **94.7%**.

The work was not eliminated; it was moved to a background worker.

``` text
Synchronous

Application thread
    │
    ├── create record
    ├── format
    ├── slow destination
    └── return
```

``` text
Asynchronous

Application thread
    │
    ├── create record
    ├── enqueue record
    └── return

Background worker
    │
    ├── format
    ├── slow destination
    └── finish
```

### Conclusion

The current asynchronous architecture is performing its intended job. No
micro-optimization to `AsyncHandler` is justified by this evidence.

# Current conclusions

### Cheap rejection matters

``` text
Filtered DEBUG
47.42 µs → 0.25 µs
99.47% reduction
```

### Async logging is about latency isolation

Under a deliberately slow destination:

``` text
Synchronous application cost
1596.38 µs/op

Asynchronous application cost
84.46 µs/op
```

The expensive work still happens, but it no longer blocks the
application thread.

# Future benchmark areas

Potential future measurements include high-concurrency logging, queue
contention, bounded queue behavior, dropped-record policies, rotating
files, colored formatting, large structured metadata, exception
formatting, hierarchy traversal, and very high log volume.

Benchmarks should answer concrete engineering questions rather than
exist merely to increase coverage.

> **Never optimize a number. Optimize a demonstrated bottleneck.**