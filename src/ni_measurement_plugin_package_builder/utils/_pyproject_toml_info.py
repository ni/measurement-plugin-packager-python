"""Getting measurement information from pyproject.toml file."""

import re
from logging import Logger
from pathlib import Path
from typing import Any, Dict

import tomli

from ni_measurement_plugin_package_builder.constants import (
    DEFAULT_AUTHOR,
    DEFAULT_DESCRIPTION,
    DEFAULT_VERSION,
    PyProjectToml,
    UserMessages,
)
from ni_measurement_plugin_package_builder.models import PackageInfo

UNDERSCORE_SPACE_REGEX = r"[_ ]"


def get_pyproject_toml_info(pyproject_toml_path: Path) -> Dict[str, Any]:
    """Get `pyproject.toml` information.

    Args:
        pyproject_toml_path (str): File path of pyproject.toml.

    Returns:
        Dict[str, Any]: Pyproject toml information.
    """
    with open(pyproject_toml_path, "rb") as file:
        pyproject_data = tomli.load(file)

    return pyproject_data


def get_updated_package_data(
    logger: Logger,
    pyproject_toml_data: Dict[str, Any],
    measurement_name: str,
) -> PackageInfo:
    """Get updated package data from `pyproject toml` data.

    Args:
        logger (Logger): Logger object.
        pyproject_toml_data (Dict[str, str]): Pyproject toml data.
        measurement_name (str): Measurement name.

    Returns:
        PackageInfo: Updated measurement package info.
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

    updated_package_info = PackageInfo(
        measurement_name=measurement_name,
        package_name=package_name,
        description=package_description,
        version=package_version,
        author=measurement_author,
    )

    return updated_package_info


def get_measurement_package_info(measurement_plugin_path: Path, logger: Logger) -> PackageInfo:
    """Get measurement package information from pyproject.toml.

    Args:
        measurement_plugin_path (str): Measurement Plug-in path.
        logger (Logger): Logger object.

    Returns:
       PackageInfo: Measurement package info.
    """
    pyproject_toml_path = Path(measurement_plugin_path) / PyProjectToml.FILE_NAME
    measurement_name = Path(measurement_plugin_path).name

    pyproject_toml_data = get_pyproject_toml_info(pyproject_toml_path=pyproject_toml_path)

    measurement_package_info = get_updated_package_data(
        logger=logger,
        pyproject_toml_data=pyproject_toml_data,
        measurement_name=measurement_name,
    )

    return measurement_package_info
