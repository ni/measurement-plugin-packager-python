"""Implementation of interactive mode for NI measurement plugin package builder."""

from logging import Logger

from ni_measurement_plugin_package_builder.constants import YES, InteractiveModeMessages
from ni_measurement_plugin_package_builder.models import InvalidInputError, SystemLinkConfig, UploadPackageInfo
from ni_measurement_plugin_package_builder.utils._helpers import publish_meas_packages
from ._user_inputs import get_user_input_for_upload_packages, get_user_inputs_in_interactive_mode


def publish_meas_packages_in_interactive_mode(
    logger: Logger,
    measurement_plugin_base_path: str,
) -> None:
    """Publish Measurement Packages in interactive mode.

    Args:
        logger (Logger): Logger object.
        measurement_plugin_base_path (str): Measurement plugins parent path.

    Raises:
        InvalidInputError: If API Key and Feed Name not provided by the user.
    """
    upload_packages = input(InteractiveModeMessages.UPLOAD_PACKAGE).strip().lower()
    systemlink_config = SystemLinkConfig()
    upload_package_info = UploadPackageInfo()

    if upload_packages == YES:
        upload_packages = True
        systemlink_config, upload_package_info = get_user_input_for_upload_packages()
    else:
        upload_packages = False

    while True:
        measurement_plugins = get_user_inputs_in_interactive_mode(
            logger=logger,
            measurement_plugins_base_path=measurement_plugin_base_path,
        )
        if not measurement_plugins:
            break

        publish_meas_packages(
            logger=logger,
            measurement_plugin_base_path=measurement_plugin_base_path,
            measurement_plugins=measurement_plugins,
            upload_packages=upload_packages,
            systemlink_config=systemlink_config,
            upload_package_info=upload_package_info,
        )
        logger.info("\n")
        user_input_for_continuation = input(
            InteractiveModeMessages.CONTINUE_BUILDING
        ).strip().lower()

        if user_input_for_continuation != YES:
            break

        if upload_packages:
            user_input_for_same_feed = input(InteractiveModeMessages.SAME_FEED)

            if user_input_for_same_feed != YES:
                feed_name = input(InteractiveModeMessages.ENTER_FEED_NAME).strip()
                if not feed_name:
                    raise InvalidInputError(InteractiveModeMessages.NO_FEED_NAME)
                overwrite_packages = input(
                    InteractiveModeMessages.OVERWRITE_MEAS
                ).strip().lower() == YES
                upload_package_info.feed_name = feed_name
                upload_package_info.overwrite_packages = overwrite_packages

        else:
            upload_packages = input(InteractiveModeMessages.UPLOAD_PACKAGE)
            if upload_packages == YES:
                upload_packages = True
                systemlink_config, upload_package_info = get_user_input_for_upload_packages()
            else:
                upload_packages = False
