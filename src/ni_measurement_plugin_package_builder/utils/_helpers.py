"""Helper functions for NI Measurement Plugin Package Builder."""

import os
import subprocess
from logging import FileHandler, Logger
from pathlib import Path
from typing import List, Union

from nisystemlink_feeds_manager.clients.core import ApiException
from nisystemlink_feeds_manager.clients.feeds.models import UploadPackageResponse
from nisystemlink_feeds_manager.main import PublishPackagesToSystemLink
from nisystemlink_feeds_manager.models import PackageInfo

from ni_measurement_plugin_package_builder.constants import NIPKG_EXE, PACKAGES, UserMessages
from ni_measurement_plugin_package_builder.models import SystemLinkConfig, UploadPackageInfo
from ni_measurement_plugin_package_builder.utils._create_files import create_template_folders
from ._pyproject_toml_info import get_measurement_package_info
from ._validate_files import validate_meas_plugin_files


def get_folders(folder_path: str, logger: Logger) -> List[str]:
    """Get list of folders present in a path.

    Args:
        folder_path (str): Folder path provided by the user.
        logger (Logger): Logger object.

    Returns:
        List[str]: List of folders.
    """
    try:
        folders = [
            name
            for name in os.listdir(folder_path)
            if os.path.isdir(os.path.join(folder_path, name))
            and validate_meas_plugin_files(os.path.join(folder_path, name), logger)
        ]
        return folders

    except FileNotFoundError as exp:
        raise FileNotFoundError(UserMessages.INVALID_BASE_DIR.format(dir=folder_path)) from exp


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


def get_file_path(folder_path: str, file_name: str) -> str:
    """Searches for a file in the specified folder that contains the given file name.

    Args:
        folder_path (str): Folder path.
        file_name (str): File name.

    Returns:
        str: File path.
    """
    file_path = None
    for name in os.listdir(folder_path):
        if file_name in name:
            file_path = os.path.join(folder_path, name)
            break

    return file_path


def publish_package_to_systemlink(
    systemlink_config: SystemLinkConfig,
    meas_package_path: str,
    upload_package_info: UploadPackageInfo,
) -> UploadPackageResponse:
    """Publish package to SystemLink feeds services.

    Args:
        systemlink_config (SystemLinkConfig): SystenLink config credentials.
        meas_package_path (str): Measurement package path.
        upload_package_info (UploadPackageInfo): Information about the package to be uploaded.

    Returns:
        UploadPackageResponse: Uploaded measurement package response from server.
    """
    publish_packages = PublishPackagesToSystemLink(
        server_api_key=systemlink_config.api_key,
        server_url=systemlink_config.api_url,
        workspace_name=systemlink_config.workspace,
    )

    upload_response = publish_packages.upload_package(
        package_info=PackageInfo(
            feed_name=upload_package_info.feed_name,
            path=meas_package_path,
            overwrite=upload_package_info.overwrite_packages
        )
    )

    return upload_response


def build_meas_package(logger: Logger, measurement_plugin_path: str) -> Union[str, None]:
    """Build measurement plugin as NI package file.

    Args:
        logger (Logger): Logger object.
        measurement_plugin_path (str): Measurement plugin path.

    Returns:
        Union[str, None]: Built measurement package file path.
    """
    logger.info("")
    measurement_plugin = Path(measurement_plugin_path).name
    logger.info(UserMessages.BUILDING_MEAS.format(name=measurement_plugin))

    mlink_package_builder_path = get_ni_mlink_package_builder_path(logger=logger)
    if not validate_meas_plugin_files(path=measurement_plugin_path, logger=logger):
        logger.info(UserMessages.INVALID_MEAS_PLUGIN)
        return None

    measurement_package_info = get_measurement_package_info(
        measurement_plugin_path=measurement_plugin_path,
        logger=logger,
    )
    template_folder_path = create_template_folders(
        mlink_package_builder_path=mlink_package_builder_path,
        measurement_plugin_path=measurement_plugin_path,
        measurement_package_info=measurement_package_info,
    )

    package_folder_path = os.path.join(mlink_package_builder_path, PACKAGES)
    os.makedirs(package_folder_path, exist_ok=True)

    logger.info(UserMessages.TEMPLATE_FILES_COMPLETED)
    subprocess.run(f"{NIPKG_EXE} pack {template_folder_path} {package_folder_path}", check=True)
    logger.info(
        UserMessages.PACKAGE_BUILT.format(
            name=measurement_package_info.measurement_name,
            dir=package_folder_path,
        )
    )

    measurement_package_path = get_file_path(
        package_folder_path,
        measurement_package_info.measurement_name
    )
    return measurement_package_path


def publish_meas_packages(
    logger: Logger,
    measurement_plugin_base_path: str,
    measurement_plugins: List[str],
    upload_packages: bool,
    systemlink_config: SystemLinkConfig = SystemLinkConfig(),
    upload_package_info: UploadPackageInfo = UploadPackageInfo(),
) -> None:
    """Build set of measurement packages as NI package files and publish it to SystemLink feeds.

    Args:
        logger (Logger): Logger object.
        measurement_plugin_base_path (str): Measurement plugin base path.
        measurement_plugins (List[str]): List of measurement plugins.
        upload_packages (bool): True if the packages need to be uploaded to SystemLink else False.
        systemlink_config (SystemLinkConfig, optional): SystemLink config credentials. Defaults to SystemLinkConfig(). # noqa: W505
        upload_package_info (UploadPackageInfo, optional): Information about the package to be uploaded. Defaults to UploadPackageInfo(). # noqa: W505

    Returns:
        None.
    """
    for measurement_plugin in measurement_plugins:
        measurement_plugin_path = os.path.join(measurement_plugin_base_path, measurement_plugin)
        try:
            measurement_package_path = build_meas_package(
                logger=logger,
                measurement_plugin_path=measurement_plugin_path,
            )
            if upload_packages:
                upload_response = publish_package_to_systemlink(
                    systemlink_config=systemlink_config,
                    upload_package_info=upload_package_info,
                    meas_package_path=measurement_package_path,
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

        except KeyError as ex:
            logger.info(
                UserMessages.PACKAGE_UPLOAD_FAILED.format(
                    package=measurement_plugin,
                    name=upload_package_info.feed_name,
                )
            )
            logger.debug(ex, exc_info=True)
            logger.info(UserMessages.API_URL_KEY_MISSING.format(key=ex))
            logger.info(UserMessages.CHECK_LOG_FILE)

        except FileNotFoundError as ex:
            logger.info(
                UserMessages.PACKAGE_UPLOAD_FAILED.format(
                    package=measurement_plugin,
                    name=upload_package_info.feed_name,
                )
            )
            logger.debug(ex, exc_info=True)
            logger.info(ex)

        except Exception as ex:
            logger.debug(ex, exc_info=True)
            logger.info(ex)
            logger.info(UserMessages.CHECK_LOG_FILE)
