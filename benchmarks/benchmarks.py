from __future__ import annotations

import time
import timeit
from pathlib import Path
from tempfile import TemporaryDirectory

from pylog import configure, get_logger, shutdown
from pylog.filters import LevelFilter
from pylog.formatter import JsonFormatter
from pylog.handlers import (
    AsyncHandler,
    ConsoleHandler,
    FileHandler,
)
from pylog.levels import LogLevel


ITERATIONS = 10_000


def benchmark(
    name: str,
    function,
    *,
    number: int = ITERATIONS,
) -> float:
    elapsed = timeit.timeit(
        function,
        number=number,
    )

    per_operation = elapsed / number

    print(
        f"{name:<30}"
        f"{elapsed:>10.4f}s"
        f"{per_operation * 1_000_000:>12.2f} µs/op"
    )

    return elapsed


def benchmark_record_creation() -> None:
    from pylog.caller_info import CallerInspector
    from pylog.record_factory import LogRecordFactory

    factory = LogRecordFactory(
        CallerInspector()
    )

    benchmark(
        "Record creation",
        lambda: factory.create(
            level=LogLevel.INFO,
            logger_name="benchmark",
            message="benchmark",
        ),
    )


def benchmark_filtered_logging() -> None:
    configure(
        level=LogLevel.DEBUG,
        handlers=[],
    )

    logger = get_logger(
        "benchmark.filtered",
        filters=[
            LevelFilter(LogLevel.ERROR),
        ],
    )

    benchmark(
        "Filtered DEBUG",
        lambda: logger.debug("ignored"),
    )

    shutdown()


def benchmark_json_formatting() -> None:
    formatter = JsonFormatter()

    configure(
        handlers=[],
    )

    logger = get_logger(
        "benchmark.json",
    )

    record = logger._record_factory.create(
        level=LogLevel.INFO,
        logger_name="benchmark.json",
        message="benchmark",
    )

    benchmark(
        "JSON formatting",
        lambda: formatter.format(record),
    )

    shutdown()


def benchmark_file_logging() -> None:
    with TemporaryDirectory() as directory:
        path = Path(directory) / "benchmark.log"

        logger = get_logger(
            "benchmark.file",
            handlers=[
                FileHandler(path),
            ],
        )

        benchmark(
            "File logging",
            lambda: logger.info("benchmark"),
        )

        logger.close()


def benchmark_async_logging() -> None:
    with TemporaryDirectory() as directory:
        path = Path(directory) / "benchmark.log"

        handler = AsyncHandler(
            FileHandler(path)
        )

        logger = get_logger(
            "benchmark.async",
            handlers=[handler],
        )

        application_time = benchmark(
            "Async application",
            lambda: logger.info("benchmark"),
        )

        completion_start = time.perf_counter()

        logger.close()

        completion_time = (
            time.perf_counter()
            - completion_start
        )

        total_time = (
            application_time
            + completion_time
        )

        print(
            f"{'Async completion wait':<30}"
            f"{completion_time:>10.4f}s"
            f"{completion_time / ITERATIONS * 1_000_000:>12.2f} µs/op"
        )

        print(
            f"{'Async total':<30}"
            f"{total_time:>10.4f}s"
            f"{total_time / ITERATIONS * 1_000_000:>12.2f} µs/op"
        )


def benchmark_sync_vs_async() -> None:
    print()
    print("Synchronous vs Asynchronous")
    print("-" * 58)

    with TemporaryDirectory() as directory:
        sync_path = Path(directory) / "sync.log"
        async_path = Path(directory) / "async.log"

        sync_logger = get_logger(
            "benchmark.sync",
            handlers=[
                FileHandler(sync_path),
            ],
        )

        async_handler = AsyncHandler(
            FileHandler(async_path)
        )

        async_logger = get_logger(
            "benchmark.async.compare",
            handlers=[
                async_handler,
            ],
        )

        sync_time = benchmark(
            "Synchronous logging",
            lambda: sync_logger.info("benchmark"),
        )

        async_time = benchmark(
            "Asynchronous logging",
            lambda: async_logger.info("benchmark"),
        )

        async_flush_start = time.perf_counter()

        async_logger.close()

        async_flush_time = (
            time.perf_counter()
            - async_flush_start
        )

        sync_logger.close()

        print()
        print(
            f"Synchronous application time : "
            f"{sync_time:.4f}s"
        )

        print(
            f"Asynchronous application time: "
            f"{async_time:.4f}s"
        )

        print(
            f"Async completion wait         : "
            f"{async_flush_time:.4f}s"
        )

        print(
            f"Async end-to-end time         : "
            f"{async_time + async_flush_time:.4f}s"
        )

def benchmark_slow_sync_vs_async() -> None:
    from benchmarks.slow_handler import SlowHandler

    print()
    print("Slow handler: synchronous vs asynchronous")
    print("-" * 58)

    sync_logger = get_logger(
        "benchmark.slow.sync",
        handlers=[
            SlowHandler(0.001),
        ],
    )

    async_logger = get_logger(
        "benchmark.slow.async",
        handlers=[
            AsyncHandler(
                SlowHandler(0.001)
            )
        ],
    )

    sync_time = benchmark(
        "Slow synchronous",
        lambda: sync_logger.info("benchmark"),
        number=1_000,
    )

    async_time = benchmark(
        "Slow asynchronous",
        lambda: async_logger.info("benchmark"),
        number=1_000,
    )

    start = time.perf_counter()

    async_logger.close()

    async_wait = time.perf_counter() - start

    sync_logger.close()

    print()
    print(
        f"Synchronous application time : "
        f"{sync_time:.4f}s"
    )

    print(
        f"Asynchronous application time: "
        f"{async_time:.4f}s"
    )

    print(
        f"Async completion wait         : "
        f"{async_wait:.4f}s"
    )

def benchmark_context_logging() -> None:
    configure(
        handlers=[],
    )

    logger = get_logger(
        "benchmark.context",
    )

    def log_with_context() -> None:
        with logger.context(
            request_id="req-123",
            user_id=42,
        ):
            logger.info("benchmark")

    benchmark(
        "Context logging",
        log_with_context,
    )

    shutdown()


def main() -> None:
    print()
    print(
        f"{'Benchmark':<30}"
        f"{'Total':>10}"
        f"{'Per operation':>16}"
    )
    print("-" * 58)

    benchmark_record_creation()
    benchmark_filtered_logging()
    benchmark_json_formatting()
    benchmark_file_logging()
    benchmark_async_logging()
    benchmark_context_logging()

    benchmark_sync_vs_async()
    benchmark_slow_sync_vs_async()


if __name__ == "__main__":
    main()