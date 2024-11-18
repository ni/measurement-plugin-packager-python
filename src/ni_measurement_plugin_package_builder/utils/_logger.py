"""A module to initialize logger functions."""

import logging
import logging.handlers
import sys
from logging import Logger, StreamHandler
from pathlib import Path
from typing import Tuple

from ni_measurement_plugin_package_builder.constants import (
    LOG_DATE_FORMAT,
    LOG_FILE_COUNT_LIMIT,
    LOG_FILE_MSG_FORMAT,
    LOG_FILE_NAME,
    LOG_FILE_SIZE_LIMIT_IN_BYTES,
    UserMessages,
)
from ni_measurement_plugin_package_builder.utils._log_file_path import (
    get_log_folder_path,
)


def __create_file_handler(
    log_folder_path: Path,
    file_name: str,
) -> logging.handlers.RotatingFileHandler:
    log_file = Path(log_folder_path) / file_name
    folder_path_obj = Path(log_folder_path)

    if not folder_path_obj.exists():
        folder_path_obj.mkdir(parents=True)

    handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_FILE_SIZE_LIMIT_IN_BYTES,
        backupCount=LOG_FILE_COUNT_LIMIT,
    )
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(LOG_FILE_MSG_FORMAT, datefmt=LOG_DATE_FORMAT)
    handler.setFormatter(formatter)

    return handler


def __create_stream_handler() -> StreamHandler:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    return handler


def add_file_handler(logger: Logger, log_folder_path: Path) -> None:
    """Add file handler.

    Args:
        logger (Logger): Logger object.
        log_folder_path (Path): Log folder path.

    Returns:
        None.
    """
    handler = __create_file_handler(log_folder_path=log_folder_path, file_name=LOG_FILE_NAME)
    logger.addHandler(handler)


def setup_logger_with_file_handler(output_path: Path, logger: Logger) -> Tuple[Logger, Path]:
    """Adds a file handler to the provided logger.

    Args:
        output_path (Path): Output path
        logger (Logger): Logger object.

    Returns:
        Tuple[Logger, Path]: Logger object and logger folder path.
    """
    log_folder_path, public_path_status, user_path_status = get_log_folder_path(output_path)
    add_file_handler(logger=logger, log_folder_path=log_folder_path)

    if not public_path_status:
        logger.info(UserMessages.FAILED_PUBLIC_DIR)
    if not user_path_status:
        logger.info(UserMessages.FAILED_USER_DIR)

    return logger, log_folder_path


def add_stream_handler(logger: Logger) -> None:
    """Add stream handler.

    Args:
        logger (Logger): Logger object.

    Returns:
        None.
    """
    stream_handler = __create_stream_handler()
    logger.addHandler(stream_handler)


def initialize_logger(name: str) -> Logger:
    """Initialize logger object for logging.

    Args:
        name (str): Logger name.

    Returns:
        Logger: Logger object.
    """
    new_logger = logging.getLogger(name)
    new_logger.setLevel(logging.DEBUG)

    add_stream_handler(logger=new_logger)
    return new_logger


def remove_handlers(log: Logger) -> None:
    """Remove Log Handlers.

    Args:
        logger (Logger): Logger object.

    Returns:
        None.
    """
    for handler in log.handlers:
        log.removeHandler(handler)
