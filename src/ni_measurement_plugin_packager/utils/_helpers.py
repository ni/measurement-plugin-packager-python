"""Helper functions for Measurement Plug-In Package Builder."""

import subprocess  # nosec: B404
import sys
from logging import FileHandler, Logger
from pathlib import Path
from typing import Dict, List, Optional

import winreg
from nisystemlink_feeds_manager.clients.core import ApiException
from nisystemlink_feeds_manager.clients.feeds.models import UploadPackageResponse
from nisystemlink_feeds_manager.main import PublishPackagesToSystemLink
from nisystemlink_feeds_manager.models import PackageInfo

from ni_measurement_plugin_packager.constants import (
    PACKAGES,
    FileNames,
    InteractiveModeMessages,
    NonInteractiveModeMessages,
    PyProjectToml,
    UserMessages,
)
from ni_measurement_plugin_packager.models import (
    InvalidInputError,
    SystemLinkConfig,
    UploadPackageInfo,
)
from ni_measurement_plugin_packager.utils._create_files import (
    create_template_folders,
)
from ni_measurement_plugin_packager.utils._pyproject_toml_info import (
    get_measurement_package_info,
)


def _get_nipkg_exe_directory() -> Path:
    return _get_nipath("NIDIR64") / "NI Package Manager" / "nipkg.exe"


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


def is_valid_folder(folder_path: Path) -> bool:
    """Check if the provided folder path is valid or not.

    Args:
        folder_path: Folder path.

    Returns:
        True, if valid folder path. Else, False.
    """
    return folder_path.is_dir()


def display_available_measurements(logger: Logger, measurement_plugins: List[Path]) -> None:
    """Display available measurement plug-ins in CLI.

    Args:
        logger: Logger object.
        measurement_plugins: List of measurement plug-ins.
    """
    logger.info("\n")
    logger.info(InteractiveModeMessages.AVAILABLE_MEASUREMENTS)
    for index, measurement_name in enumerate(measurement_plugins):
        logger.info(f"{index + 1}. {measurement_name}")
    logger.info("")


def validate_plugin_files(plugin_path: Path, logger: Logger) -> bool:
    """Validate measurement plug-in files.

    Args:
        plugin_path: Measurement plug-in path.
        logger: Logger object.

    Returns:
        True, if measurement plug-in folder is valid. Else, False.
    """
    pyproject_path: Path = plugin_path / PyProjectToml.FILE_NAME
    measurement_file_path: Path = plugin_path / FileNames.MEASUREMENT_FILE
    batch_file_path: Path = plugin_path / FileNames.BATCH_FILE
    valid_file: bool = True

    if not pyproject_path.is_file():
        logger.debug(UserMessages.NO_TOML_FILE.format(dir=plugin_path))
        valid_file = False

    if not measurement_file_path.is_file():
        logger.debug(UserMessages.NO_MEAS_FILE.format(dir=plugin_path))
        valid_file = False

    if not batch_file_path.is_file():
        logger.debug(UserMessages.NO_BATCH_FILE.format(dir=plugin_path))
        valid_file = False

    return valid_file


def validate_selected_plugins(
    selected_plugins: str,
    measurement_plugins: List[Path],
    logger: Logger,
) -> None:
    """Validate the selected measurement plug-ins in `non-interactive mode`.

    Args:
        selected_plugins: User selected measurement plug-ins.
        measurement_plugins: Measurement plug-ins.
        logger: Logger object.

    Raises:
        InvalidInputError: if any invalid input in the selected measurement plug-ins.
    """
    for measurement_plugin in selected_plugins.split(","):
        plugin_name = measurement_plugin.strip("'\"").strip()

        if plugin_name not in measurement_plugins:
            display_available_measurements(logger=logger, measurement_plugins=measurement_plugins)

            raise InvalidInputError(
                NonInteractiveModeMessages.INVALID_SELECTED_PLUGINS.format(input=plugin_name)
            )


def get_measurement_plugins(measurement_plugins: List[Path]) -> Dict[str, Path]:
    """Get measurement plug-ins with indexes.

    Args:
        measurement_plugins: List of measurement plug-ins.

    Returns:
        Measurement plug-ins with indexes.
    """
    measurement_plugins_with_indexes = {}
    for index, measurement_name in enumerate(measurement_plugins):
        measurement_plugins_with_indexes[str(index + 1)] = measurement_name

    return measurement_plugins_with_indexes


def get_folders(folder_path: Path, logger: Logger) -> List[Path]:
    """Get list of folders present in a path.

    Args:
        folder_path: Folder path provided by the user.
        logger: Logger object.

    Returns:
        List of folders.
    """
    try:
        folders = [
            name
            for name in folder_path.iterdir()
            if (folder_path / name).is_dir()
            and validate_plugin_files(folder_path / name, logger)
        ]
        return folders

    except FileNotFoundError as exp:
        raise FileNotFoundError(UserMessages.INVALID_BASE_DIR.format(dir=folder_path)) from exp


def get_ni_package_builder_path(logger: Logger) -> Optional[Path]:
    """Get Folder path of `Measurement Plug-in Package Builder`.

    Args:
        logger: Logger object.

    Returns:
        Folder path.
    """
    for handler in logger.handlers:
        if isinstance(handler, FileHandler):
            folder_two_levels_up = Path(handler.baseFilename).resolve().parent.parent
            return folder_two_levels_up

    return None


def get_file_path(folder_path: Path, file_name: str) -> Optional[Path]:
    """Searches for a file in the specified folder that contains the given file name.

    Args:
        folder_path: Folder path.
        file_name: File name.

    Returns:
        File path.
    """
    file_path = None
    for name in folder_path.iterdir():
        if file_name in str(name):
            file_path = folder_path / name
            break

    return file_path


def publish_package_to_systemlink(
    publish_package_client: PublishPackagesToSystemLink,
    package_path: Path,
    upload_package_info: UploadPackageInfo,
) -> UploadPackageResponse:
    """Publish package to SystemLink feeds services.

    Args:
        publish_package_client: Client for publish packages to SystemLink.
        package_path: Measurement package path.
        upload_package_info: Information about the package to be uploaded.

    Returns:
        Uploaded measurement package response from server.
    """
    upload_response = publish_package_client.upload_package(
        package_info=PackageInfo(
            feed_name=upload_package_info.feed_name,
            path=package_path,
            overwrite=upload_package_info.overwrite_packages,
        )
    )

    return upload_response


def get_publish_package_client(
    systemlink_config: SystemLinkConfig,
    logger: Logger,
) -> PublishPackagesToSystemLink:
    """Get publish package client for uploading the measurement packages.

    Args:
        systemlink_config: SystemLink configuration credentials.
        logger: Logger object.

    Returns:
        Client for publishing the packages to SystemLink.
    """
    try:
        publish_package_client = PublishPackagesToSystemLink(
            server_api_key=systemlink_config.api_key,
            server_url=systemlink_config.api_url,
            workspace_name=systemlink_config.workspace,
        )
        return publish_package_client

    except KeyError as ex:
        logger.info(UserMessages.FAILED_CLIENT_CREATION)
        logger.debug(ex, exc_info=True)
        logger.info(UserMessages.API_URL_KEY_MISSING.format(key=ex))
        logger.info(UserMessages.CHECK_LOG_FILE)

    except FileNotFoundError as ex:
        logger.info(UserMessages.FAILED_CLIENT_CREATION)
        logger.debug(ex, exc_info=True)
        logger.info(ex)

    except ApiException as ex:
        logger.info(ex.error.message)
        logger.info(UserMessages.CHECK_LOG_FILE)


def build_package(logger: Logger, measurement_plugin_path: Path) -> Optional[Path]:
    """Build measurement plug-in as NI package file.

    Args:
        logger: Logger object.
        measurement_plugin_path: Measurement plug-in path.

    Returns:
        Built measurement package file path.
    """
    logger.info("")
    measurement_plugin = Path(measurement_plugin_path).name
    logger.info(UserMessages.BUILDING_MEAS.format(name=measurement_plugin))

    plugin_package_builder_path = get_ni_package_builder_path(logger=logger)
    if not plugin_package_builder_path:
        logger.info(UserMessages.INVALID_BUILDER_PATH)
        return None

    if not validate_plugin_files(plugin_path=measurement_plugin_path, logger=logger):
        logger.info(UserMessages.INVALID_MEAS_PLUGIN)
        return None

    measurement_package_info = get_measurement_package_info(
        measurement_plugin_path=measurement_plugin_path,
        logger=logger,
    )
    template_folder_path = create_template_folders(
        plugin_package_builder_path=plugin_package_builder_path,
        measurement_plugin_path=measurement_plugin_path,
        measurement_package_info=measurement_package_info,
    )

    package_folder_path = Path(plugin_package_builder_path) / PACKAGES
    package_folder_path.mkdir(parents=True, exist_ok=True)

    logger.info(UserMessages.TEMPLATE_FILES_COMPLETED)
    path_to_nipkg_exe = _get_nipkg_exe_directory()
    command = f"{path_to_nipkg_exe} pack {template_folder_path} {package_folder_path}"
    subprocess.run(command, shell=False, check=True)  # nosec: B603
    logger.info(
        UserMessages.PACKAGE_BUILT.format(
            name=measurement_package_info.measurement_name,
            dir=package_folder_path,
        )
    )

    measurement_package_path = get_file_path(
        package_folder_path,
        measurement_package_info.package_name,
    )
    return measurement_package_path


def publish_packages(
    logger: Logger,
    measurement_plugin_base_path: Path,
    measurement_plugins: List[str],
    publish_package_client: PublishPackagesToSystemLink,
    upload_package_info: UploadPackageInfo,
) -> None:
    """Build set of measurement packages as NI package files and publish it to SystemLink feeds.

    Args:
        logger: Logger object.
        measurement_plugin_base_path: Measurement plug-in base path.
        measurement_plugins: List of measurement plug-ins.
        publish_package_client: Client for publish packages to SystemLink.
        upload_package_info: Information about the package to be uploaded.
    """
    for measurement_plugin in measurement_plugins:
        measurement_plugin_path = Path(measurement_plugin_base_path) / measurement_plugin
        try:
            measurement_package_path = build_package(
                logger=logger,
                measurement_plugin_path=measurement_plugin_path,
            )
            if publish_package_client and measurement_package_path:
                upload_response = publish_package_to_systemlink(
                    publish_package_client=publish_package_client,
                    package_path=measurement_package_path,
                    upload_package_info=upload_package_info,
                )
                logger.info(
                    UserMessages.PACKAGE_UPLOADED.format(
                        package_name=upload_response.file_name,
                        feed_name=upload_package_info.feed_name,
                    )
                )
        except ApiException as ex:
            logger.debug(ex, exc_info=True)
            logger.info(
                UserMessages.PACKAGE_UPLOAD_FAILED.format(
                    package=measurement_plugin,
                    name=upload_package_info.feed_name,
                )
            )
            logger.info(ex.error.message)
            logger.info(UserMessages.CHECK_LOG_FILE)

        except (KeyError, FileNotFoundError) as ex:
            logger.debug(ex, exc_info=True)
            logger.info(ex)
            logger.info(UserMessages.CHECK_LOG_FILE)

        except Exception as ex:
            logger.debug(ex, exc_info=True)
            logger.info(ex)
            logger.info(UserMessages.CHECK_LOG_FILE)
