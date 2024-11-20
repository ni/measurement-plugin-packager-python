"""Implementation of non-interactive mode for Measurement Plug-In Package Builder."""

from logging import Logger
from pathlib import Path
from typing import List

from nisystemlink_feeds_manager.main import PublishPackagesToSystemLink

from ni_measurement_plugin_packager._support._helpers import (
    get_folders,
    publish_packages,
    validate_selected_plugins,
)
from ni_measurement_plugin_packager.constants import UserMessages
from ni_measurement_plugin_packager.models import InvalidInputError, UploadPackageInfo


def publish_packages_in_non_interactive_mode(
    logger: Logger,
    measurement_plugin_base_path: Path,
    selected_plugins: str,
    publish_package_client: PublishPackagesToSystemLink,
    upload_package_info: UploadPackageInfo,
) -> None:
    """Publish measurement packages in non interactive mode.

    Args:
        logger: Logger object.
        measurement_plugin_base_path: Measurement plugins root folder path.
        selected_plugins: Selected measurement plugins.
        publish_package_client: Client for publish packages to SystemLink.
        upload_package_info: Information about the package to be uploaded.

    Raises:
        InvalidInputError: If API Key and Feed Name not provided by the user.
    """
    measurement_plugins: list[Path] = get_folders(
        folder_path=measurement_plugin_base_path, logger=logger
    )

    if not measurement_plugins:
        raise InvalidInputError(
            UserMessages.INVALID_BASE_DIR.format(dir=measurement_plugin_base_path)
        )

    plugins_to_process: List[str]
    if selected_plugins == ".":
        plugins_to_process = [str(path) for path in measurement_plugins]
    else:
        validate_selected_plugins(
            measurement_plugins=measurement_plugins,
            selected_plugins=selected_plugins,
            logger=logger,
        )
        plugins_to_process = [plugin.strip("'\"").strip() for plugin in selected_plugins.split(",")]

    publish_packages(
        logger=logger,
        measurement_plugin_base_path=measurement_plugin_base_path,
        measurement_plugins=plugins_to_process,
        publish_package_client=publish_package_client,
        upload_package_info=upload_package_info,
    )
    logger.info("")