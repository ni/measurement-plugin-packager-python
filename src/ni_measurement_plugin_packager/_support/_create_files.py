"""Helper functions for creating the files for Measurement Plug-In Package Builder."""

import platform
import shutil
import sys
from pathlib import Path

import winreg

from ni_measurement_plugin_packager.constants import (
    ControlFile,
    FileNames,
    InstructionFile,
)
from ni_measurement_plugin_packager.models import PackageInfo

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


def _get_measurement_services_path(measurement_name: str) -> Path:
    return _get_nipath("NIPUBAPPDATADIR") / "Plug-Ins" / "Measurements" / measurement_name


def _get_nipath(name: str) -> Path:
    if sys.platform == "win32":
        access: int = winreg.KEY_READ
        if "64" in name:
            access |= winreg.KEY_WOW64_64KEY
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\National Instruments\Common\Installer",
            access=access,
        ) as key:
            value, type = winreg.QueryValueEx(key, name)
            assert type == winreg.REG_SZ  # nosec: B101
            return Path(value)


def _get_system_type() -> str:
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


def copy_folder_contents(src_path: Path, dest_path: Path) -> None:
    """Copy contents of folders to destination, excluding specified files/folders.

    Args:
        src_path: Source folder path.
        dest_path: Destination folder path.
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
    plugin_package_builder_path: Path,
    measurement_plugin_path: Path,
    measurement_package_info: PackageInfo,
) -> Path:
    """Create Template folders for building NI Packages.

    Args:
        plugin_package_builder_path: Measurement Package builder path.
        measurement_plugin_path: Measurement Plugin path from user.
        measurement_package_info: Measurement package information.

    Returns:
        Template folder path.
    """
    template_path = Path(plugin_package_builder_path) / measurement_package_info.measurement_name

    if template_path.is_dir():
        shutil.rmtree(template_path)

    data_path = template_path / FileNames.DATA
    template_measurement_folder_path = data_path / measurement_package_info.package_name

    control_path = template_path / FileNames.CONTROL

    control_path.mkdir(parents=True, exist_ok=True)
    template_measurement_folder_path.mkdir(parents=True, exist_ok=True)

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

    debian_binary_file = template_path / FileNames.DEBIAN_BIN
    with open(debian_binary_file, "w", encoding="utf-8") as fp:
        fp.write("2.0")

    return template_path


def create_control_file(control_folder_path: Path, package_info: PackageInfo) -> None:
    """Create control file for storing information about measurement package.

    Args:
        control_folder_path: Control folder path.
        package_info: Measurement Package information.
    """
    control_file_path = control_folder_path / FileNames.CONTROL

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
    control_file_data += ControlFile.ARCHITECTURE + ": " + _get_system_type() + "\n"
    control_file_data += ControlFile.DESCRIPTION + ": " + package_description + "\n"
    control_file_data += ControlFile.VERSION + ": " + package_version + "\n"
    control_file_data += ControlFile.XB_DISPLAY_NAME + ": " + measurement_name + "\n"
    control_file_data += ControlFile.MAINTAINER + ": " + measurement_author + "\n"
    control_file_data += ControlFile.PACKAGE + ": " + package_name + "\n"

    with open(control_file_path, "w", encoding="utf-8") as fp:
        fp.write(control_file_data)


def create_instruction_file(data_path: Path, measurement_name: str, package_name: str) -> None:
    """Create instruction file for storing measurement directory information.

    Args:
        data_path: Data folder path.
        measurement_name: Measurement service name.
        package_name: Measurement package name.
    """
    measurement_service_path = _get_measurement_services_path(measurement_name=measurement_name)
    instruction_path = data_path / InstructionFile.INSTRUCTION

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
        + str(measurement_service_path)
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
