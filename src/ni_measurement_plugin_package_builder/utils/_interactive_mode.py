"""Implementation of interactive mode for NI Measurement Plug-In Package builder."""

from logging import Logger
from pathlib import Path

from ni_measurement_plugin_package_builder.constants import InteractiveModeMessages
from ni_measurement_plugin_package_builder.models import (
    SystemLinkConfig,
    UploadPackageInfo,
)
from ni_measurement_plugin_package_builder.utils._helpers import (
    get_publish_package_client,
    publish_meas_packages,
)
from ni_measurement_plugin_package_builder.utils._user_inputs import (
    get_feed_name,
    get_user_input_for_upload_packages,
    get_user_inputs_in_interactive_mode,
    get_yes_no_response,
)


def __update_upload_package_inputs(upload_package_info: UploadPackageInfo) -> UploadPackageInfo:
    user_input_for_same_feed = get_yes_no_response(InteractiveModeMessages.SAME_FEED)

    if not user_input_for_same_feed:
        feed_name = get_feed_name()
        overwrite_packages = get_yes_no_response(InteractiveModeMessages.OVERWRITE_MEAS)
        upload_package_info.feed_name = feed_name
        upload_package_info.overwrite_packages = overwrite_packages

    return upload_package_info


def publish_meas_packages_in_interactive_mode(
    logger: Logger,
    measurement_plugin_base_path: Path,
) -> None:
    """Publish Measurement Packages in interactive mode.

    Args:
        logger (Logger): Logger object.
        measurement_plugin_base_path (str): Measurement plug-ins parent path.

    Raises:
        InvalidInputError: If API Key and Feed Name not provided by the user.
    """
    systemlink_config = SystemLinkConfig()
    upload_package_info = UploadPackageInfo()
    publish_package_client = None
    upload_packages = get_yes_no_response(InteractiveModeMessages.UPLOAD_PACKAGE)

    if upload_packages:
        systemlink_config, upload_package_info = get_user_input_for_upload_packages(logger)
        publish_package_client = get_publish_package_client(
            systemlink_config=systemlink_config,
            logger=logger,
        )

    while True:
        measurement_plugins = get_user_inputs_in_interactive_mode(
            logger=logger,
            measurement_plugins_base_path=measurement_plugin_base_path,
        )
        if not measurement_plugins:
            break

        plugins_to_process = [str(path) for path in measurement_plugins]
        publish_meas_packages(
            logger=logger,
            measurement_plugin_base_path=measurement_plugin_base_path,
            measurement_plugins=plugins_to_process,
            publish_package_client=publish_package_client,
            upload_package_info=upload_package_info,
        )
        logger.info("\n")
        user_input_for_continuation = get_yes_no_response(InteractiveModeMessages.CONTINUE_BUILDING)

        if not user_input_for_continuation:
            break

        if upload_packages:
            upload_package_info = __update_upload_package_inputs(upload_package_info)
