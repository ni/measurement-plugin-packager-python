"""Implementation of Command Line Interface."""

import os
import re
from logging import Logger
from typing import Any, Dict, List, Union

import tomli

from ni_measurement_plugin_package_builder.constants import (
    DEFAULT_AUTHOR,
    DEFAULT_DESCRIPTION,
    DEFAULT_VERSION,
    MEASUREMENT_NAME,
    PyProjectToml,
    UserMessages,
)

ALL_MEAS = "."
UNDERSCORE_SPACE_REGEX = r"[_ ]"


def __read_pyproject_toml(pyproject_toml_path: str) -> Dict[str, Any]:
    with open(pyproject_toml_path, "rb") as file:
        pyproject_data = tomli.load(file)

    return pyproject_data


def get_updated_package_data(
    logger: Logger,
    pyproject_toml_data: Dict[str, str],
    measurement_name: str,
) -> Dict[str, str]:
    """Get updated package data from `pyproject toml` data.

    Args:
        logger (Logger): Logger object.
        pyproject_toml_data (Dict[str, str]): Pyproject toml data.
        measurement_name (str): Measurement name.

    Returns:
        Dict[str, str]: Updated measurement package info.
    """
    package_info = pyproject_toml_data[PyProjectToml.TOOL][PyProjectToml.POETRY]
    package_description = package_info[PyProjectToml.DESCRIPTION]
    package_name = package_info[PyProjectToml.NAME].lower()
    package_version = package_info[PyProjectToml.VERSION]
    measurement_author = package_info[PyProjectToml.AUTHOR]

    if not package_name:
        package_name = measurement_name
        package_name = re.sub(UNDERSCORE_SPACE_REGEX, "-", package_name)
        logger.info(UserMessages.EMPTY_NAME.format(name=package_name))

    if not package_description:
        package_description = DEFAULT_DESCRIPTION
        logger.info(UserMessages.EMPTY_DESCRIPTION.format(description=DEFAULT_DESCRIPTION))

    if not package_version:
        package_version = DEFAULT_VERSION
        logger.info(UserMessages.EMPTY_VERSION.format(version=DEFAULT_VERSION))

    if not measurement_author:
        measurement_author = DEFAULT_AUTHOR
        logger.info(UserMessages.EMPTY_AUTHOR.format(author=DEFAULT_AUTHOR))
    else:
        measurement_author = ",".join(author for author in measurement_author)

    package_name = re.sub(UNDERSCORE_SPACE_REGEX, "-", package_name)

    updated_package_info = {
        MEASUREMENT_NAME: measurement_name,
        PyProjectToml.NAME: package_name,
        PyProjectToml.DESCRIPTION: package_description,
        PyProjectToml.VERSION: package_version,
        PyProjectToml.AUTHOR: measurement_author,
    }

    return updated_package_info


def get_measurement_package_info(measurement_plugin_path: str, logger: Logger) -> Dict[str, str]:
    """Get measurement package information from pyproject.toml.

    Args:
        measurement_plugin_path (str): Measurement Plugin path.
        logger (Logger): Logger object.

    Returns:
        Dict[str, str]: Measurement package info.
    """
    pyproject_toml_path = os.path.join(measurement_plugin_path, PyProjectToml.FILE_NAME)
    measurement_name = os.path.basename(measurement_plugin_path)

    pyproject_toml_data = __read_pyproject_toml(pyproject_toml_path=pyproject_toml_path)

    measurement_package_info = get_updated_package_data(
        logger=logger,
        pyproject_toml_data=pyproject_toml_data,
        measurement_name=measurement_name,
    )

    return measurement_package_info


def get_folders(folder_path: str) -> List[str]:
    """Get list of folders present in a path.

    Args:
        folder_path (str): Folder path provided by the user.

    Returns:
        List[str]: List of folders.
    """
    try:
        folders = [
            name
            for name in os.listdir(folder_path)
            if os.path.isdir(os.path.join(folder_path, name))
        ]
        return folders

    except FileNotFoundError as exp:
        raise FileNotFoundError(UserMessages.INVALID_BASE_DIR.format(dir=folder_path)) from exp


def get_user_inputs_in_interactive_mode(
    logger: Logger,
    measurement_plugins_base_path: str,
) -> Union[List[str], None]:
    """Get user inputs for measurement package builder in `interactive mode`.

    Args:
        logger (Logger): Logger object.
        measurement_plugins_base_path (str): Measurement plugin base path.

    Returns:
        Union[List[str], None]: User selected measurement infomation.
    """
    measurement_plugins_list = get_folders(measurement_plugins_base_path)

    if not measurement_plugins_list:
        raise FileNotFoundError(
            UserMessages.INVALID_BASE_DIR.format(dir=measurement_plugins_base_path)
        )

    logger.info("\n")
    logger.info(UserMessages.AVAILABLE_MEASUREMENTS)
    logger.info("\n")

    measurement_plugins = {}
    for index, measurement_name in enumerate(measurement_plugins_list):
        logger.info(f"{index + 1}.{measurement_name}")
        measurement_plugins[str(index + 1)] = measurement_name

    logger.info("\n")
    user_warning_count = 2

    while user_warning_count > 0:
        user_selected_plugin_numbers = input(
            UserMessages.MEASUREMENT_NUMBER.format(start=1, end=len(measurement_plugins_list))
        ).strip().split(",")

        if user_selected_plugin_numbers == [ALL_MEAS]:
            user_selected_measurements = list(measurement_plugins.values())
            return user_selected_measurements

        selected_measurements = []
        for user_selected_plugin_number in user_selected_plugin_numbers:
            if user_selected_plugin_number in measurement_plugins:
                selected_measurements.append(measurement_plugins[user_selected_plugin_number])

        if selected_measurements:
            return selected_measurements

        logger.info(UserMessages.INVALID_INPUT)
        user_warning_count -= 1

    return None
