"""A module to initialize and manage logger configurations."""

import logging
import logging.handlers
import sys
from logging import Logger, StreamHandler
from pathlib import Path
from typing import Tuple

from ni_measurement_plugin_packager._support._log_file_path import get_log_directory_path
from ni_measurement_plugin_packager.constants import (
    LOG_DATE_FORMAT,
    LOG_FILE_COUNT_LIMIT,
    LOG_FILE_MSG_FORMAT,
    LOG_FILE_NAME,
    LOG_FILE_SIZE_LIMIT_IN_BYTES,
    StatusMessages,
)


def _setup_file_handler(
    log_directory_path: Path,
    file_name: str,
) -> logging.handlers.RotatingFileHandler:
    log_file = Path(log_directory_path) / file_name
    directory_path_obj = Path(log_directory_path)

    if not directory_path_obj.exists():
        directory_path_obj.mkdir(parents=True)

    handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_FILE_SIZE_LIMIT_IN_BYTES,
        backupCount=LOG_FILE_COUNT_LIMIT,
    )
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(LOG_FILE_MSG_FORMAT, datefmt=LOG_DATE_FORMAT)
    handler.setFormatter(formatter)

    return handler


def _setup_stream_handler() -> StreamHandler:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    return handler


def add_file_handler(logger: Logger, log_directory_path: Path) -> None:
    """Add a file handler to the logger for logging to a file.

    Args:
        logger: Logger object.
        log_directory_path: Log directory path.
    """
    handler = _setup_file_handler(log_directory_path=log_directory_path, file_name=LOG_FILE_NAME)
    logger.addHandler(handler)


def setup_logger_with_file_handler(fallback_path: Path, logger: Logger) -> Tuple[Logger, Path]:
    """Set up a logger with a file handler, returning the logger and log directory path.

    Args:
        fallback_path: Output path
        logger: Logger object.

    Returns:
        Logger object and logger directory path.
    """
    log_directory_path, public_path_status, user_path_status = get_log_directory_path(fallback_path)
    add_file_handler(logger=logger, log_directory_path=log_directory_path)

    if not public_path_status:
        logger.info(StatusMessages.PUBLIC_DIRECTORY_INACCESSIBLE)
    if not user_path_status:
        logger.info(StatusMessages.USER_DIRECTORY_INACCESSIBLE)

    return logger, log_directory_path


def add_stream_handler(logger: Logger) -> None:
    """Add a stream handler to the logger for logging to the console.

    Args:
        logger: Logger object.
    """
    stream_handler = _setup_stream_handler()
    logger.addHandler(stream_handler)


def initialize_logger(name: str) -> Logger:
    """Initialize and configure a logger with stream and file handlers.

    Args:
        name: Logger name.

    Returns:
        Logger object.
    """
    new_logger = logging.getLogger(name)
    new_logger.setLevel(logging.DEBUG)

    add_stream_handler(logger=new_logger)
    return new_logger


def remove_handlers(logger: Logger) -> None:
    """Remove all handlers from the given logger.

    Args:
        logger: Logger object.
    """
    for handler in logger.handlers:
        logger.removeHandler(handler)
