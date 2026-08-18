from __future__ import annotations
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
) -> None:
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

    logger = get_logger(
        "benchmark.json",
        handlers=[
            ConsoleHandler(
                formatter=formatter,
            )
        ],
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

        benchmark(
            "Async logging",
            lambda: logger.info("benchmark"),
        )

        logger.close()


def benchmark_context_logging() -> None:
    configure(
        handlers=[],
    )

    logger = get_logger("benchmark.context")

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


if __name__ == "__main__":
    main()