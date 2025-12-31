"""
Async Logger initialization module for the application.
Logs messages to console, file (if configured), and Discord (for warnings and above) asynchronously.
"""

import asyncio
import base64
import logging
from typing import Optional

import aiohttp
from aiohttp import ClientTimeout
from redis.asyncio import Redis
from redis.asyncio.sentinel import Sentinel

from app.core.config import get_settings
from app.interfaces.redis_config import redis_args

settings = get_settings()


def get_sentinel():
    sentinel = Sentinel(settings.redis.sentinels, **redis_args)
    return sentinel.master_for("mymaster", **redis_args)


redis_conn = get_sentinel() if settings.redis.sentinels else Redis(**redis_args)
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
            record.levelname = self.DISCORD_MAP.get(record.levelno, record.levelname)
        else:
            record.levelname = self.COLOR_MAP.get(record.levelno, record.levelname)
        return super().format(record)


# --- Async Discord Notification ---
async def send_discord_message(msg: str, timeout: int = 5) -> None:
    url = settings.discord.webhook_url.get_secret_value().strip()
    payload = {
        "content": f"{settings.discord.prefix} : {msg}",
    }
    try:
        timeout_cfg = ClientTimeout(total=timeout)
        async with aiohttp.ClientSession(timeout=timeout_cfg) as session:
            async with session.post(url, json=payload) as resp:
                if resp.status != 204:
                    logging.error("Discord webhook failed with status %s", resp.status)
    except Exception as ex:
        logging.error("Error sending Discord notification: %s", ex)


class DiscordLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()

    def emit(self, record: logging.LogRecord) -> None:
        if record.levelno >= logging.WARNING:
            msg = self.format(record)
            loop = asyncio.get_running_loop()
            loop.create_task(self.add_message(msg))

    async def add_message(self, msg: str) -> None:
        msg_b_64 = base64.b64encode(msg.encode())
        redis_key = f"LLM_SERVICE:LOGGING:DISCORD_THRESHOLD:{msg_b_64}"
        key_check = await redis_conn.hgetall(redis_key)
        if key_check:
            return
        async with redis_conn.pipeline(transaction=True) as pipe:
            await pipe.hset(redis_key, "", "")
            await pipe.expire(redis_key, 3600)
            await pipe.execute()

        await send_discord_message(msg)


# --- Logger Initialization ---
def init_logger(name: str) -> logging.Logger:
    """Initialize and return a logger with console, file, and optional async Discord handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(settings.log_level)
    logger.propagate = False  # Prevent double logging from root logger

    formatter = MultiTargetFormatter(
        "%(asctime)s [ %(levelname)s ] [%(name)s %(lineno)d] %(message)s"
    )
    formatter_discord = MultiTargetFormatter(
        "[ %(levelname)s ] [%(name)s %(lineno)d] %(message)s", discord_mode=True
    )

    # File handler
    if settings.log_file:
        file_handler = logging.FileHandler(settings.log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Console handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # Discord handler
    if settings.discord.enable:
        discord_handler = DiscordLogHandler()
        discord_handler.setFormatter(formatter_discord)
        logger.addHandler(discord_handler)

    return logger
