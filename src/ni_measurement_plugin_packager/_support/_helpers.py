"""Helper functions for Measurement Plug-In Packager."""

import subprocess  # nosec: B404
from logging import FileHandler, Logger
from pathlib import Path
from typing import List, Optional

from nisystemlink_feeds_manager.clients.core import ApiException
from nisystemlink_feeds_manager.clients.feeds.models import UploadPackageResponse
from nisystemlink_feeds_manager.main import PublishPackagesToSystemLink
from nisystemlink_feeds_manager.models import PackageInfo

from ni_measurement_plugin_packager._constants import (
    PACKAGES,
    CommandLinePrompts,
    FileNames,
    PyProjectToml,
    StatusMessages,
)
from ni_measurement_plugin_packager._support import _get_nipath
from ni_measurement_plugin_packager._support._create_files import (
    generate_template_directories,
)
from ni_measurement_plugin_packager._support._pyproject_toml_info import (
    get_plugin_package_info,
)


def _get_nipkg_exe_directory() -> Path:
    return _get_nipath("NIDIR64") / "NI Package Manager" / "nipkg.exe"


def _list_available_plugins_in_root_directory(
    logger: Logger, measurement_plugins: List[Path]
) -> None:
    logger.info(CommandLinePrompts.AVAILABLE_PLUGINS)
    for index, plugin_name in enumerate(measurement_plugins):
        logger.info(f"{index + 1}. {plugin_name}")


def _is_valid_plugin_directory(plugin_path: Path, logger: Logger) -> bool:
    pyproject_path: Path = plugin_path / PyProjectToml.FILE_NAME
    measurement_file_path: Path = plugin_path / FileNames.MEASUREMENT_FILE
    batch_file_path: Path = plugin_path / FileNames.BATCH_FILE
    valid_file: bool = True

    if not pyproject_path.is_file():
        logger.debug(StatusMessages.MISSING_TOML_FILE.format(dir=plugin_path))
        valid_file = False

    if not measurement_file_path.is_file():
        logger.debug(StatusMessages.MISSING_MEASUREMENT_FILE.format(dir=plugin_path))
        valid_file = False

    if not batch_file_path.is_file():
        logger.debug(StatusMessages.MISSING_BATCH_FILE.format(dir=plugin_path))
        valid_file = False

    return valid_file


def _validate_selected_plugins(
    selected_plugins: str,
    measurement_plugins: List[Path],
    logger: Logger,
) -> None:
    for measurement_plugin in selected_plugins.split(","):
        plugin_name = measurement_plugin.strip("'\"").strip()

        if plugin_name not in str(measurement_plugins):
            _list_available_plugins_in_root_directory(
                logger=logger, measurement_plugins=measurement_plugins
            )

            raise ValueError(CommandLinePrompts.SELECTED_PLUGINS_INVALID.format(input=plugin_name))


def _get_valid_plugin_directories(directory_path: Path, logger: Logger) -> List[Path]:
    try:
        directories = [
            name
            for name in directory_path.iterdir()
            if (directory_path / name).is_dir()
            and _is_valid_plugin_directory(directory_path / name, logger)
        ]
        return directories

    except FileNotFoundError as exp:
        raise FileNotFoundError(
            StatusMessages.INVALID_ROOT_DIRECTORY.format(dir=directory_path)
        ) from exp


def _get_packager_root_directory(logger: Logger) -> Optional[Path]:
    for handler in logger.handlers:
        if isinstance(handler, FileHandler):
            directory_two_levels_up = Path(handler.baseFilename).resolve().parent.parent
            return directory_two_levels_up

    return None


def _find_file_in_directory(directory_path: Path, file_name: str) -> Optional[Path]:
    file_path = None
    for name in directory_path.iterdir():
        if file_name in str(name):
            file_path = directory_path / name
            break

    return file_path


def _build_and_upload_packages(
    logger: Logger,
    plugin_root_directory: Path,
    measurement_plugins: List[str],
    systemlink_client: PublishPackagesToSystemLink,
    feed_name: Optional[str],
    overwrite_packages: Optional[bool],
) -> None:
    for measurement_plugin in measurement_plugins:
        measurement_plugin_path = Path(plugin_root_directory) / measurement_plugin
        try:
            measurement_package_path = build_package(
                logger=logger,
                plugin_path=measurement_plugin_path,
            )
            if systemlink_client and measurement_package_path:
                upload_response = upload_to_systemlink_feed(
                    systemlink_client=systemlink_client,
                    package_path=measurement_package_path,
                    feed_name=feed_name,
                    overwrite_packages=overwrite_packages,
                )
                logger.info(
                    StatusMessages.PACKAGE_UPLOADED.format(
                        package_name=upload_response.file_name,
                        feed_name=feed_name,
                    )
                )
        except ApiException as ex:
            logger.debug(ex, exc_info=True)
            logger.info(
                StatusMessages.UPLOAD_FAILED.format(
                    package=measurement_plugin,
                    name=feed_name,
                )
            )
            logger.info(ex.error.message)
            logger.info(StatusMessages.CHECK_LOG_FILE)

        except (KeyError, FileNotFoundError) as ex:
            logger.debug(ex, exc_info=True)
            logger.info(ex)
            logger.info(StatusMessages.CHECK_LOG_FILE)

        except Exception as ex:
            logger.debug(ex, exc_info=True)
            logger.info(ex)
            logger.info(StatusMessages.CHECK_LOG_FILE)


def upload_to_systemlink_feed(
    systemlink_client: PublishPackagesToSystemLink,
    package_path: Path,
    feed_name: Optional[str],
    overwrite_packages: Optional[bool],
) -> UploadPackageResponse:
    """Upload a package to SystemLink feeds.

    Args:
        systemlink_client: Client for publish packages to SystemLink.
        package_path: Measurement package path.
        feed_name: Name of the feed to upload to.
        overwrite_packages: Whether to overwrite existing packages.

    Returns:
        Uploaded measurement package response from server.
    """
    upload_response = systemlink_client.upload_package(
        package_info=PackageInfo(
            feed_name=feed_name,
            path=str(package_path),
            overwrite=overwrite_packages,
        )
    )

    return upload_response


def initialize_systemlink_client(
    api_key: Optional[str],
    api_url: Optional[str],
    workspace: Optional[str],
    logger: Logger,
) -> PublishPackagesToSystemLink:
    """Initialize a client to upload packages to SystemLink.

    Args:
        api_key: SystemLink API key.
        api_url: SystemLink API URL.
        workspace: SystemLink workspace name.
        logger: Logger object.

    Returns:
        Client for publishing the packages to SystemLink.
    """
    try:
        systemlink_client = PublishPackagesToSystemLink(
            server_api_key=api_key,
            server_url=api_url,
            workspace_name=workspace,
        )
        return systemlink_client

    except KeyError as ex:
        logger.info(StatusMessages.CLIENT_CREATION_FAILED)
        logger.debug(ex, exc_info=True)
        logger.info(StatusMessages.API_URL_KEY_MISSING.format(key=ex))
        logger.info(StatusMessages.CHECK_LOG_FILE)

    except FileNotFoundError as ex:
        logger.info(StatusMessages.CLIENT_CREATION_FAILED)
        logger.debug(ex, exc_info=True)
        logger.info(ex)

    except ApiException as ex:
        logger.info(ex.error.message)
        logger.info(StatusMessages.CHECK_LOG_FILE)


def process_and_upload_packages(
    logger: Logger,
    plugin_root_directory: Path,
    selected_plugins: str,
    systemlink_client: PublishPackagesToSystemLink,
    feed_name: Optional[str],
    overwrite_packages: Optional[bool],
) -> None:
    """Build and publish selected measurement packages.

    Args:
        logger: Logger object.
        plugin_root_directory: Measurement plugins root directory path.
        selected_plugins: Selected measurement plugins.
        systemlink_client: Client for publish packages to SystemLink.
        feed_name: Name of the feed to upload to.
        overwrite_packages: Whether to overwrite existing packages.

    Raises:
        FileNotFoundError: If no valid plugins are found in the directory.
    """
    measurement_plugins: list[Path] = _get_valid_plugin_directories(
        directory_path=plugin_root_directory, logger=logger
    )

    if not measurement_plugins:
        raise FileNotFoundError(
            StatusMessages.INVALID_ROOT_DIRECTORY.format(dir=plugin_root_directory)
        )

    plugins_to_process: List[str]
    if selected_plugins == ".":
        plugins_to_process = [str(path) for path in measurement_plugins]
    else:
        _validate_selected_plugins(
            measurement_plugins=measurement_plugins,
            selected_plugins=selected_plugins,
            logger=logger,
        )
        plugins_to_process = [plugin.strip("'\"").strip() for plugin in selected_plugins.split(",")]

    _build_and_upload_packages(
        logger=logger,
        plugin_root_directory=plugin_root_directory,
        measurement_plugins=plugins_to_process,
        systemlink_client=systemlink_client,
        feed_name=feed_name,
        overwrite_packages=overwrite_packages,
    )


def build_package(logger: Logger, plugin_path: Path) -> Optional[Path]:
    """Build a .nipkg file for the given plug-in.

    Args:
        logger: Logger object.
        measurement_plugin_path: Measurement plug-in path.

    Returns:
        Built measurement package file path.
    """
    measurement_plugin = Path(plugin_path).name
    logger.info(StatusMessages.BUILDING_PACKAGE.format(name=measurement_plugin))

    packager_root_directory = _get_packager_root_directory(logger=logger)
    if not packager_root_directory:
        logger.info(StatusMessages.INVALID_PACKAGER_PATH)
        return None

    if not _is_valid_plugin_directory(plugin_path=plugin_path, logger=logger):
        logger.info(StatusMessages.INVALID_PLUGIN)
        return None

    measurement_package_info = get_plugin_package_info(
        measurement_plugin_path=plugin_path,
        logger=logger,
    )
    template_directory_path = generate_template_directories(
        packager_root_directory=packager_root_directory,
        measurement_plugin_path=plugin_path,
        measurement_package_info=measurement_package_info,
    )

    package_directory_path = Path(packager_root_directory) / PACKAGES
    package_directory_path.mkdir(parents=True, exist_ok=True)

    logger.info(StatusMessages.TEMPLATE_FILES_GENERATED)
    path_to_nipkg_exe = _get_nipkg_exe_directory()
    command = f"{path_to_nipkg_exe} pack {template_directory_path} {package_directory_path}"
    subprocess.run(command, shell=False, check=True)  # nosec: B603
    logger.info(
        StatusMessages.PACKAGE_BUILT.format(
            name=measurement_package_info.plugin_name,
            dir=package_directory_path,
        )
    )

    measurement_package_path = _find_file_in_directory(
        package_directory_path,
        measurement_package_info.package_name,
    )
    return measurement_package_path
