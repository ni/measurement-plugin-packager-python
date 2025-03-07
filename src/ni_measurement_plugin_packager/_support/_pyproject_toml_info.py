"""Module for extracting and processing measurement information from pyproject.toml."""

import re
from logging import Logger
from pathlib import Path
from typing import Any, Dict

import tomli

from ni_measurement_plugin_packager._constants import (
    PyProjectToml,
    StatusMessages,
)
from ni_measurement_plugin_packager._support._package_info import PackageInfo

UNDERSCORE_SPACE_REGEX = r"[_ ]"
DEFAULT_DESCRIPTION = "Python Measurement Plug-In"
DEFAULT_VERSION = "1.0.0"
DEFAULT_AUTHOR = "National Instruments"


def _parse_pyproject_toml(toml_file_path: Path) -> Dict[str, Any]:
    with open(toml_file_path, "rb") as file:
        pyproject_data = tomli.load(file)

    return pyproject_data


def _extract_package_metadata(
    logger: Logger,
    toml_content: Dict[str, Any],
    plugin_name: str,
) -> PackageInfo:
    package_info = toml_content[PyProjectToml.TOOL][PyProjectToml.POETRY]
    package_description = package_info[PyProjectToml.DESCRIPTION]
    package_name = package_info[PyProjectToml.NAME].lower()
    package_version = package_info[PyProjectToml.VERSION]
    package_author = package_info[PyProjectToml.AUTHOR]

    if not package_name:
        package_name = plugin_name
        package_name = re.sub(UNDERSCORE_SPACE_REGEX, "-", package_name)
        logger.info(StatusMessages.NO_NAME.format(name=package_name))

    if not package_description:
        package_description = DEFAULT_DESCRIPTION
        logger.info(StatusMessages.NO_DESCRIPTION.format(description=DEFAULT_DESCRIPTION))

    if not package_version:
        package_version = DEFAULT_VERSION
        logger.info(StatusMessages.NO_VERSION.format(version=DEFAULT_VERSION))

    if not package_author:
        package_author = DEFAULT_AUTHOR
        logger.info(StatusMessages.NO_AUTHOR.format(author=DEFAULT_AUTHOR))
    else:
        package_author = ",".join(author for author in package_author)

    package_name = re.sub(UNDERSCORE_SPACE_REGEX, "-", package_name)

    updated_package_info = PackageInfo(
        plugin_name=plugin_name,
        package_name=package_name,
        description=package_description,
        version=package_version,
        author=package_author,
    )

    return updated_package_info


def get_plugin_package_info(measurement_plugin_path: Path, logger: Logger) -> PackageInfo:
    """Retrieve package information from the measurement plug-in directory.

    Args:
        measurement_plugin_path: Measurement Plug-in path.
        logger: Logger object.

    Returns:
       Measurement package info.
    """
    pyproject_toml_path = Path(measurement_plugin_path) / PyProjectToml.FILE_NAME
    plugin_name = Path(measurement_plugin_path).name

    pyproject_toml_data = _parse_pyproject_toml(toml_file_path=pyproject_toml_path)

    measurement_package_info = _extract_package_metadata(
        logger=logger,
        toml_content=pyproject_toml_data,
        plugin_name=plugin_name,
    )

    return measurement_package_info
