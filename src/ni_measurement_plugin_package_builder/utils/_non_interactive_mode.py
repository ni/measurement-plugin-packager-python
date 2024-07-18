"""Implementation of non-interactive mode for NI measurement plugin package builder."""

from logging import Logger

from nisystemlink_feeds_manager.main import PublishPackagesToSystemLink

from ni_measurement_plugin_package_builder.constants import UserMessages
from ni_measurement_plugin_package_builder.models import (
    InvalidInputError,
    UploadPackageInfo,
)
from ni_measurement_plugin_package_builder.utils._helpers import (
    get_folders,
    publish_meas_packages,
    validate_selected_meas_plugins,
)


def publish_meas_packages_in_non_interactive_mode(
    logger: Logger,
    measurement_plugin_base_path: str,
    selected_meas_plugins: str,
    publish_package_client: PublishPackagesToSystemLink,
    upload_package_info: UploadPackageInfo,
) -> None:
    """Publish measurement packages in non interactive mode.

    Args:
        logger (Logger): Logger object.
        measurement_plugin_base_path (str): Measurement plugins parent path.
        selected_meas_plugins (str): Selected measurement plugins.
        publish_package_client (PublishPackagesToSystemLink): Client for publish packages to SystemLink. # noqa:  W505
        upload_package_info (UploadPackageInfo): Information about the package to be uploaded.

    Raises:
        InvalidInputError: If API Key and Feed Name not provided by the user.
    """
    measurement_plugins = get_folders(folder_path=measurement_plugin_base_path, logger=logger)

    if not measurement_plugins:
        raise InvalidInputError(
            UserMessages.INVALID_BASE_DIR.format(dir=measurement_plugin_base_path)
        )

    if selected_meas_plugins == ".":
        selected_meas_plugins = measurement_plugins
    else:
        validate_selected_meas_plugins(
            measurement_plugins=measurement_plugins,
            selected_meas_plugins=selected_meas_plugins,
            logger=logger,
        )
        selected_meas_plugins = [
            meas_plugin.strip("'\"").strip() for meas_plugin in selected_meas_plugins.split(",")
        ]

    publish_meas_packages(
        logger=logger,
        measurement_plugin_base_path=measurement_plugin_base_path,
        measurement_plugins=selected_meas_plugins,
        publish_package_client=publish_package_client,
        upload_package_info=upload_package_info,
    )
    logger.info("")
