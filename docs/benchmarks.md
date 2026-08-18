# pylog Performance Benchmarks

## Environment

- Python: 3.13.14
- OS: macOS
- CPU: arm64
- pylog version: v3.0
- Benchmark iterations: 10,000

## Baseline

| Operation | Total | Per operation |
|---|---:|---:|
| Record creation | 0.2730s | 27.30 µs |
| Filtered DEBUG | 0.4742s | 47.42 µs |
| JSON formatting | 0.0217s | 2.17 µs |
| File logging | 0.5268s | 52.68 µs |
| Async logging | 0.6271s | 62.71 µs |
| Context logging | 0.4863s | 48.63 µs |

## Observations

### 1. Record creation

27.30 µs/op.

This includes:

- caller inspection
- timestamp creation
- process/thread identification
- context capture
- immutable metadata creation

### 2. Filtered logging

47.42 µs/op.

Potential optimization:

The current logger creates a `LogRecord` before applying
some filters. Level-based filters could potentially reject
records before record creation.

### 3. JSON formatting

2.17 µs/op.

Formatting is relatively cheap compared with record creation
and file I/O.

### 4. File logging

52.68 µs/op.

Includes formatting, locking, writing and flushing.

### 5. Async logging

62.71 µs/op.

The benchmark measures submission latency, including queue
synchronization. The purpose of async logging is not necessarily
to make the call itself cheaper, but to move formatting and I/O
off the application thread.

### 6. Context logging

48.63 µs/op.

Context creation and `ContextVar` operations contribute to the
cost.

## Methodology

Benchmarks use `timeit` with 10,000 iterations.

Optimizations should only be accepted if they preserve
correctness and demonstrate measurable improvement.

## Optimization 1 — Pre-record filtering

### Change

Added `Filter.pre_filter()` so filters capable of making a
decision from the log level or logger name can reject records
before `LogRecord` construction.

### Result

| Operation | Before | After | Improvement |
|---|---:|---:|---:|
| Filtered DEBUG | 47.42 µs | 0.25 µs | 99.47% faster |

### Correctness

All tests passed.

### Observation

The optimization removes unnecessary work including:

- Caller inspection
- Timestamp creation
- Context capture
- Metadata copying
- Immutable record construction

The optimization is especially valuable for applications where
a large percentage of log messages are filtered.