"""日志模块:控制台 + 文件双输出,记录接口请求与报错信息。"""
import logging
import os
from logging.handlers import RotatingFileHandler

from app.config import settings

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")


def setup_logger(name: str = "hospital") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler()
    console.setFormatter(fmt)
    logger.addHandler(console)

    os.makedirs(LOG_DIR, exist_ok=True)
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger()
