import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "test.log"



def get_logger(name: str) -> logging.Logger:
    """Create and configure a logger for the test framework."""

    logger = logging.getLogger(name)

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        file_handler = logging.FileHandler(
            LOG_FILE,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        logger.setLevel(logging.INFO)

    return logger


def log_separator():
    """Write a visual separator to the console and log file."""

    separator = "=" * 120

    separator_logger = logging.getLogger("separator")

    if not separator_logger.handlers:
        console_handler = logging.StreamHandler()
        file_handler = logging.FileHandler(
            LOG_FILE,
            encoding="utf-8"
        )

        console_handler.setFormatter(logging.Formatter("%(message)s"))
        file_handler.setFormatter(logging.Formatter("%(message)s"))

        separator_logger.addHandler(console_handler)
        separator_logger.addHandler(file_handler)

        separator_logger.setLevel(logging.INFO)

    separator_logger.info(separator)
