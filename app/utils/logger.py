"""
Async Logger initialization module for the application.
Logs messages to console, file (if configured), and Discord (for warnings and above) asynchronously.
"""

import logging
from typing import Optional
from app.core.config import settings


logging.getLogger("passlib").setLevel(logging.ERROR)


class MultiTargetFormatter(logging.Formatter):
    """Formatter that supports console colors and Discord-friendly text."""

    COLOR_MAP = {
        logging.DEBUG: "\033[34mDEBUG\033[0m",  # Blue
        logging.INFO: "\033[32mINFO\033[0m",  # Green
        logging.WARNING: "\033[33mWARNING\033[0m",  # Yellow
        logging.ERROR: "\033[91mERROR\033[0m",  # Bright Red
        logging.CRITICAL: "\033[31mCRITICAL\033[0m",  # Red
    }

    DISCORD_MAP = {
        logging.DEBUG: "🐛 DEBUG",
        logging.INFO: "ℹ️ INFO",
        logging.WARNING: "⚠️ WARNING",
        logging.ERROR: "🚨 ERROR",
        logging.CRITICAL: "💀 CRITICAL",
    }

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        discord_mode: bool = False,
    ):
        super().__init__(fmt, datefmt)
        self.discord_mode = discord_mode

    def format(self, record: logging.LogRecord) -> str:
        if self.discord_mode:
            record.levelname = self.DISCORD_MAP.get(
                record.levelno, record.levelname)
        else:
            record.levelname = self.COLOR_MAP.get(
                record.levelno, record.levelname)
        return super().format(record)


# --- Logger Initialization ---
def init_logger(name: str) -> logging.Logger:
    """Initialize and return a logger with console, file, and optional async Discord handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(settings.log_level)
    logger.propagate = False  # Prevent double logging from root logger

    formatter = MultiTargetFormatter(
        "%(asctime)s [ %(levelname)s ] [%(name)s %(lineno)d] %(message)s"
    )

    # File handler
    # if settings.log_file:
    #     file_handler = logging.FileHandler(settings.log_file)
    #     file_handler.setFormatter(formatter)
    #     logger.addHandler(file_handler)

    # Console handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger
