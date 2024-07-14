"""Helper functions for fetching and validating the files for NI Measurement Plugin Package Builder.
"""

import os
from logging import FileHandler, Logger
from typing import List, Union

from ni_measurement_plugin_package_builder.constants import (
    BATCH_FILE,
    MEASUREMENT_FILE,
    PyProjectToml,
    UserMessages,
)
from ni_measurement_plugin_package_builder.models import InvalidInputError


def get_ni_mlink_package_builder_path(logger: Logger) -> Union[str, None]:
    """Get Folder path of `NI MeasurementLink Package Builder`.

    Args:
        logger (Logger): Logger object.

    Returns:
        Union[str, None]: Folder path.
    """
    for handler in logger.handlers:
        if isinstance(handler, FileHandler):
            folder_two_levels_up = os.path.abspath(os.path.join(handler.baseFilename, "../../"))
            return folder_two_levels_up

    return None


def validate_meas_plugin_files(path: str, logger: Logger) -> bool:
    """Validate Measurement Plugin files.

    Args:
        path (str): Measurement Plugin path.
        logger (Logger): Logger object.

    Returns:
        bool: True if valid measurement plugin folder else False.
    """
    pyproject_path = os.path.join(path, PyProjectToml.FILE_NAME)
    measurement_file_path = os.path.join(path, MEASUREMENT_FILE)
    batch_file_path = os.path.join(path, BATCH_FILE)
    valid_file = True

    if not os.path.isfile(pyproject_path):
        logger.info(UserMessages.NO_TOML_FILE.format(dir=path))
        valid_file = False

    if not os.path.isfile(measurement_file_path):
        logger.info(UserMessages.NO_MEAS_FILE.format(dir=path))
        valid_file = False

    if not os.path.isfile(batch_file_path):
        logger.info(UserMessages.NO_BATCH_FILE.format(dir=path))
        valid_file = False

    return valid_file


def validate_selected_meas_plugins(
    selected_meas_plugins: str,
    measurement_plugins: List[str],
    logger: Logger,
) -> None:
    """Validate the selected measurement plugins.

    Args:
        selected_meas_plugins (str): User selected measurement plugins.
        measurement_plugins (List[str]): Measurement plugins.
        logger (Logger): Logger object.

    Raises:
        InvalidInputError: if any invalid input in the selected measurement plugins.

    Returns:
        None.
    """
    for measurement_plugin in selected_meas_plugins.split(","):
        plugin_name = measurement_plugin.strip("'\"").strip()

        if plugin_name not in measurement_plugins:
            logger.info("\n")
            logger.info(UserMessages.AVAILABLE_MEASUREMENTS)
            for index, measurement_name in enumerate(measurement_plugins):
                logger.info(f"{index + 1}.{measurement_name}")
            logger.info("\n")

            raise InvalidInputError(UserMessages.INVALID_SELECTED_PLUGINS.format(input=plugin_name))
