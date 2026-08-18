from pathlib import Path

from pylog import get_logger
from pylog.formatter import JsonFormatter
from pylog.handlers import (
    AsyncHandler,
    FileHandler,
    RotatingFileHandler,
)


def test_async_json_logging(tmp_path: Path) -> None:
    path = tmp_path / "app.log"

    handler = AsyncHandler(
        FileHandler(
            path,
            formatter=JsonFormatter(),
        )
    )

    logger = get_logger(
        "integration",
        handlers=[handler],
    )

    with logger.context(
        request_id="req-123",
        user_id=42,
    ):
        logger.info("Request started")

    logger.close()

    content = path.read_text()

    assert '"level": "INFO"' in content
    assert '"message": "Request started"' in content
    assert '"request_id": "req-123"' in content
    assert '"user_id": 42' in content

    def test_async_rotating_file(tmp_path: Path) -> None:
        path = tmp_path / "app.log"

        handler = AsyncHandler(
            RotatingFileHandler(
                path,
                max_bytes=500,
                backup_count=3,
            )
        )

        logger = get_logger(
            "rotation",
            handlers=[handler],
        )

        for i in range(100):
            logger.info(f"Message {i}")

        logger.close()

        files = list(tmp_path.glob("app.log*"))

        assert len(files) <= 4

from concurrent.futures import ThreadPoolExecutor


def test_concurrent_logging(tmp_path: Path) -> None:
    path = tmp_path / "concurrent.log"

    logger = get_logger(
        "concurrent",
        handlers=[
            FileHandler(path),
        ],
    )

    def worker(worker_id: int) -> None:
        for i in range(100):
            logger.info(
                f"worker={worker_id} message={i}"
            )

    with ThreadPoolExecutor(max_workers=10) as executor:
        list(
            executor.map(
                worker,
                range(10),
            )
        )

    logger.close()

    lines = path.read_text().splitlines()

    assert len(lines) == 1_000