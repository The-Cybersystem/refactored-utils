import logging
import sys
from aiologger import Logger
from aiologger.levels import LogLevel
from aiologger.formatters.base import Formatter
from aiologger.handlers.streams import AsyncStreamHandler
from aiologger.handlers.files import AsyncFileHandler


def setup_async_logger():
    """
    Configures and returns an asynchronous logger (aiologger).
    """
    logger = Logger(name="application", level=LogLevel.INFO)

    # Formatter
    formatter = Formatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Handlers
    stream_handler = AsyncStreamHandler()
    stream_handler.formatter = formatter
    logger.add_handler(stream_handler)

    file_handler = AsyncFileHandler(filename="app.log")
    file_handler.formatter = formatter
    logger.add_handler(file_handler)

    return logger

def setup_sync_logger():
    """
    Configures and returns a synchronous logger (standard logging).
    """
    logger = logging.getLogger("main")
    logger.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler
    file_handler = logging.FileHandler("main.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
