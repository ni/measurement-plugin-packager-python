"""Implementation of template creation for building NI packages."""

import os
import platform
import shutil
from pathlib import Path
from typing import Dict

from ni_measurement_plugin_package_builder.constants import (
    CONTROL,
    DATA,
    DEBIAN_BIN,
    MEASUREMENT_NAME,
    MEASUREMENT_SERVICES_PATH,
    ControlFile,
    InstructionFile,
    PyProjectToml,
)


def transfer_measurement_files(
    template_measurement_folder_path: str,
    measurement_plugin_path: str,
) -> None:
    """Transfer measurement files to template data folder.

    Args:
        template_measurement_folder_path (str): Template measurement folder path.
        measurement_plugin_path (str): Measurement plugin path from user.

    Returns:
        None.
    """
    src_path = Path(measurement_plugin_path)
    dest_path = Path(template_measurement_folder_path)

    # Iterate over all files in the source directory
    for item in src_path.iterdir():
        if item.is_file():
            shutil.copy2(item, dest_path / item.name)


def create_template_folders(
    mlink_package_builder_path: str,
    measurement_plugin_path: str,
    measurement_package_info: Dict[str, str],
) -> str:
    """Create Template folders for building NI Packages.

    Args:
        mlink_package_builder_path (str): Measurement Package builder path.
        measurement_plugin_path (str): Measurement Plugin path from user.
        measurement_package_info (Dict[str, str]): Measurement package information.

    Returns:
        str: Template folder path.
    """
    template_path = os.path.join(
        mlink_package_builder_path, measurement_package_info[MEASUREMENT_NAME]
    )
    if os.path.isdir(template_path):
        shutil.rmtree(template_path)

    data_path = os.path.join(template_path, DATA)
    template_measurement_folder_path = os.path.join(
        data_path, measurement_package_info[PyProjectToml.NAME]
    )
    control_path = os.path.join(template_path, CONTROL)

    os.makedirs(control_path, exist_ok=True)
    os.makedirs(template_measurement_folder_path, exist_ok=True)
    transfer_measurement_files(
        template_measurement_folder_path=template_measurement_folder_path,
        measurement_plugin_path=measurement_plugin_path,
    )
    create_control_file(
        control_folder_path=control_path,
        package_info=measurement_package_info,
    )
    create_instruction_file(
        data_path=data_path,
        measurement_name=measurement_package_info[MEASUREMENT_NAME],
        package_name=measurement_package_info[PyProjectToml.NAME],
    )

    debian_binary_file = os.path.join(template_path, DEBIAN_BIN)
    with open(debian_binary_file, "w", encoding="utf-8") as fp:
        fp.write("2.0")

    return template_path


def __get_system_type() -> str:
    system = platform.system().lower()
    architecture = platform.machine().lower()

    if architecture in ["amd64", "x86_64"]:
        architecture = "x64"
    elif architecture in ["x86", "i386", "i686"]:
        architecture = "x86"
    elif architecture in ["arm64", "aarch64"]:
        architecture = "arm64"
    elif architecture in ["arm", "armv7l"]:
        architecture = "arm"

    return f"{system}_{architecture}"


def create_control_file(control_folder_path: str, package_info: Dict[str, str]) -> None:
    """Create control file for storing information about measurement package.

    Args:
        control_folder_path (str): Control folder path.
        package_info (Dict[str, str]): Measurement Package information.

    Returns:
        None
    """
    control_file_path = os.path.join(control_folder_path, CONTROL)

    package_version = package_info[PyProjectToml.VERSION]
    package_description = package_info[PyProjectToml.DESCRIPTION]
    package_name = package_info[PyProjectToml.NAME].lower()
    measurement_name = package_info[MEASUREMENT_NAME]

    measurement_author = package_info[PyProjectToml.AUTHOR]

    control_file_data = ControlFile.BUILT_USING + ": " + ControlFile.NIPKG + "\n"
    control_file_data += ControlFile.SECTION + ": " + ControlFile.ADD_ONS + "\n"
    control_file_data += ControlFile.XB_PLUGIN + ": " + ControlFile.FILE + "\n"
    control_file_data += ControlFile.XB_STOREPRODUCT + ": " + ControlFile.NO + "\n"
    control_file_data += ControlFile.XB_USER_VISIBLE + ": " + ControlFile.YES + "\n"
    control_file_data += ControlFile.XB_VISIBLE_RUNTIME + ": " + ControlFile.NO + "\n"
    control_file_data += ControlFile.ARCHITECTURE + ": " + __get_system_type() + "\n"
    control_file_data += ControlFile.DESCRIPTION + ": " + package_description + "\n"
    control_file_data += ControlFile.VERSION + ": " + package_version + "\n"
    control_file_data += ControlFile.XB_DISPLAY_NAME + ": " + measurement_name + "\n"
    control_file_data += ControlFile.MAINTAINER + ": " + measurement_author + "\n"
    control_file_data += ControlFile.PACKAGE + ": " + package_name + "\n"

    with open(control_file_path, "w", encoding="utf-8") as fp:
        fp.write(control_file_data)


def create_instruction_file(data_path: str, measurement_name: str, package_name: str) -> None:
    """Create instruction file for storing measurement directory information.

    Args:
        data_path (str): Data folder path.
        measurement_name (str): Measurement service name.
        package_name (str): Measurement package name.

    Returns:
        None.
    """
    measurement_service_path = os.path.join(MEASUREMENT_SERVICES_PATH, measurement_name)
    instruction_path = os.path.join(data_path, InstructionFile.INSTRUCTION)

    instruction_data = (
        InstructionFile.START_TAG + InstructionFile.INSTRUCTION + InstructionFile.END_TAG + "\n"
    )
    instruction_data += (
        InstructionFile.START_TAG
        + InstructionFile.CUSTOM_DIRECTORIES
        + InstructionFile.END_TAG
        + "\n"
    )
    instruction_data += (
        "    "
        + InstructionFile.START_TAG
        + InstructionFile.CUSTOM_DIRECTORY
        + " "
        + InstructionFile.NAME
        + "="
        + '"'
        + package_name
        + '" '
        + InstructionFile.PATH
        + "="
        + '"'
        + measurement_service_path
        + '"'
        + InstructionFile.CLOSE_END_TAG
        + "\n"
    )
    instruction_data += (
        InstructionFile.CLOSE_START_TAG
        + InstructionFile.CUSTOM_DIRECTORIES
        + InstructionFile.END_TAG
        + "\n"
    )
    instruction_data += (
        InstructionFile.CLOSE_START_TAG + InstructionFile.INSTRUCTION + InstructionFile.END_TAG
    )

    with open(instruction_path, "w", encoding="utf-8") as fp:
        fp.write(instruction_data)
