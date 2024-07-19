"""Helper functions for creating the files for NI Measurement Plugin Package Builder."""

import os
import platform
import shutil
from pathlib import Path

from ni_measurement_plugin_package_builder.constants import (
    MEASUREMENT_SERVICES_PATH,
    ControlFile,
    FileNames,
    InstructionFile,
)
from ni_measurement_plugin_package_builder.models import PackageInfo

ignore_dirs = [
    ".venv",
    "__pycache__",
    ".cache",
    "dist",
    ".vscode",
    ".vs",
    ".env",
    "poetry.lock",
    ".mypy_cache",
    ".pytest_cache",
    "coverage.xml",
]


def copy_folder_contents(src_path: Path, dest_path: Path) -> None:
    """Copy the contents of the folders except few `files/folders` and place it in the destination path. # noqa: W505.

    Args:
        src_path (Path): Source folder path.
        dest_path (Path): Destination folder path.

    Returns:
        None.
    """
    for item in src_path.iterdir():
        if item.name in ignore_dirs:
            continue
        dest_item = dest_path / item.name
        if item.is_dir():
            dest_item.mkdir(parents=True, exist_ok=True)
            copy_folder_contents(item, dest_item)
        else:
            shutil.copy2(item, dest_item)


def create_template_folders(
    mlink_package_builder_path: str,
    measurement_plugin_path: str,
    measurement_package_info: PackageInfo,
) -> str:
    """Create Template folders for building NI Packages.

    Args:
        mlink_package_builder_path (str): Measurement Package builder path.
        measurement_plugin_path (str): Measurement Plugin path from user.
        measurement_package_info (PackageInfo): Measurement package information.

    Returns:
        str: Template folder path.
    """
    template_path = os.path.join(
        mlink_package_builder_path, measurement_package_info.measurement_name
    )
    if os.path.isdir(template_path):
        shutil.rmtree(template_path)

    data_path = os.path.join(template_path, FileNames.DATA)
    template_measurement_folder_path = os.path.join(
        data_path, measurement_package_info.package_name
    )
    control_path = os.path.join(template_path, FileNames.CONTROL)

    os.makedirs(control_path, exist_ok=True)
    os.makedirs(template_measurement_folder_path, exist_ok=True)

    copy_folder_contents(
        src_path=Path(measurement_plugin_path),
        dest_path=Path(template_measurement_folder_path),
    )
    create_control_file(
        control_folder_path=control_path,
        package_info=measurement_package_info,
    )
    create_instruction_file(
        data_path=data_path,
        measurement_name=measurement_package_info.measurement_name,
        package_name=measurement_package_info.package_name,
    )

    debian_binary_file = os.path.join(template_path, FileNames.DEBIAN_BIN)
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


def create_control_file(control_folder_path: str, package_info: PackageInfo) -> None:
    """Create control file for storing information about measurement package.

    Args:
        control_folder_path (str): Control folder path.
        package_info (PackageInfo): Measurement Package information.

    Returns:
        None
    """
    control_file_path = os.path.join(control_folder_path, FileNames.CONTROL)

    package_version = package_info.version
    package_description = package_info.description
    package_name = package_info.package_name.lower()
    measurement_name = package_info.measurement_name

    measurement_author = package_info.author

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
