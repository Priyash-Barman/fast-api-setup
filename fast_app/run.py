import subprocess
import sys
import uvicorn
from typing import NoReturn
from config import PORT, RELOAD
from fast_app.utils.logger import logger


def run_type_check() -> None:
    logger.info("🔍 Running type checks...")

    result = subprocess.run(
        ["mypy", "."],
        text=True,
        capture_output=True,
    )

    if result.returncode != 0:
        logger.error("❌ Type check FAILED\n")
        logger.error(result.stdout)
        logger.error(result.stderr)
        sys.exit(1)

    logger.info("✅ Type check PASSED\n")


def dev() -> NoReturn:
    run_type_check()

    uvicorn.run(
        "fast_app.main:app",
        port=PORT,
        reload=RELOAD,
    )

    raise SystemExit


def start() -> NoReturn:
    run_type_check()

    uvicorn.run(
        "fast_app.main:app",
        host="0.0.0.0",
        port=PORT,
        reload=False,
    )

    raise SystemExit


if __name__ == "__main__":
    dev()
