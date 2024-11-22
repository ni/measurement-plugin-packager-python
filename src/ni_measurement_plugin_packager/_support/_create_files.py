"""Helper functions for creating and managing template files for NI Packages."""

import platform
import shutil
from pathlib import Path

from ni_measurement_plugin_packager._support import _get_nipath
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


def _get_measurement_services_path(plugin_name: str) -> Path:
    return _get_nipath("NIPUBAPPDATADIR") / "Plug-Ins" / "Measurements" / plugin_name


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


def copy_directory_with_filters(source_directory: Path, destination_directory: Path) -> None:
    """Copy contents of folders to destination, excluding specified files/folders.

    Args:
        source_directory: Source folder path.
        destination_directory: Destination folder path.
    """
    for item in source_directory.iterdir():
        if item.name in ignore_dirs:
            continue
        dest_item = destination_directory / item.name
        if item.is_dir():
            dest_item.mkdir(parents=True, exist_ok=True)
            copy_directory_with_filters(item, dest_item)
        else:
            shutil.copy2(item, dest_item)


def generate_template_folders(
    packager_root_directory: Path,
    measurement_plugin_path: Path,
    measurement_package_info: PackageInfo,
) -> Path:
    """Create template folders for building NI Packages.

    Args:
        packager_root_directory: Measurement Packager path.
        measurement_plugin_path: Measurement Plugin path.
        measurement_package_info: Measurement package information.

    Returns:
        Template folder path.
    """
    template_directory = Path(packager_root_directory) / measurement_package_info.plugin_name

    if template_directory.is_dir():
        shutil.rmtree(template_directory)

    data_directory = template_directory / FileNames.DATA
    template_measurement_folder_path = data_directory / measurement_package_info.package_name

    control_folder_path = template_directory / FileNames.CONTROL

    control_folder_path.mkdir(parents=True, exist_ok=True)
    template_measurement_folder_path.mkdir(parents=True, exist_ok=True)

    copy_directory_with_filters(
        source_directory=Path(measurement_plugin_path),
        destination_directory=Path(template_measurement_folder_path),
    )
    generate_control_file(
        control_folder_path=control_folder_path,
        package_info=measurement_package_info,
    )
    generate_instruction_file(
        data_path=data_directory,
        plugin_name=measurement_package_info.plugin_name,
        package_name=measurement_package_info.package_name,
    )

    debian_binary_file = template_directory / FileNames.DEBIAN_BIN
    with open(debian_binary_file, "w", encoding="utf-8") as fp:
        fp.write("2.0")

    return template_directory


def generate_control_file(control_folder_path: Path, package_info: PackageInfo) -> None:
    """Create control file for storing information about the plugin package.

    Args:
        control_folder_path: Control folder path.
        package_info: Measurement Package information.
    """
    control_file_path = control_folder_path / FileNames.CONTROL

    control_file_data = f"""\
{ControlFile.BUILT_USING}: {ControlFile.NIPKG}
{ControlFile.SECTION}: {ControlFile.ADD_ONS}
{ControlFile.XB_PLUGIN}: {ControlFile.FILE}
{ControlFile.XB_STOREPRODUCT}: {ControlFile.NO}
{ControlFile.XB_USER_VISIBLE}: {ControlFile.YES}
{ControlFile.XB_VISIBLE_RUNTIME}: {ControlFile.NO}
{ControlFile.ARCHITECTURE}: {_get_system_type()}
{ControlFile.DESCRIPTION}: {package_info.description}
{ControlFile.VERSION}: {package_info.version}
{ControlFile.XB_DISPLAY_NAME}: {package_info.plugin_name}
{ControlFile.MAINTAINER}: {package_info.author}
{ControlFile.PACKAGE}: {package_info.package_name.lower()}"""

    with open(control_file_path, "w", encoding="utf-8") as fp:
        fp.write(control_file_data)


def generate_instruction_file(data_path: Path, plugin_name: str, package_name: str) -> None:
    """Create an instruction file for storing information about the plugin directory.

    Args:
        data_path: Data folder path.
        plugin_name: Measurement service name.
        package_name: Measurement package name.
    """
    measurement_service_path = _get_measurement_services_path(plugin_name=plugin_name)
    instruction_path = data_path / InstructionFile.INSTRUCTION

    instruction_data = f"""\
{InstructionFile.START_TAG}{InstructionFile.INSTRUCTION}{InstructionFile.END_TAG}
{InstructionFile.START_TAG}{InstructionFile.CUSTOM_DIRECTORIES}{InstructionFile.END_TAG}
    {InstructionFile.START_TAG}{InstructionFile.CUSTOM_DIRECTORY} {InstructionFile.NAME}="{package_name}" {InstructionFile.PATH}="{measurement_service_path}"{InstructionFile.CLOSE_END_TAG}
{InstructionFile.CLOSE_START_TAG}{InstructionFile.CUSTOM_DIRECTORIES}{InstructionFile.END_TAG}
{InstructionFile.CLOSE_START_TAG}{InstructionFile.INSTRUCTION}{InstructionFile.END_TAG}"""

    with open(instruction_path, "w", encoding="utf-8") as fp:
        fp.write(instruction_data)
