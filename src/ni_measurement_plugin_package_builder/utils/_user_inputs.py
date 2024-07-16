"""Implementation of Command Line Interface."""

from logging import Logger
from typing import Dict, List, Union, Tuple

from ni_measurement_plugin_package_builder.constants import InteractiveModeMessages, UserMessages, YES
from ni_measurement_plugin_package_builder.models import UploadPackageInfo, SystemLinkConfig, InvalidInputError
from ni_measurement_plugin_package_builder.utils._helpers import get_folders

ALL_MEAS = "."


def validate_user_input_for_meas_plugins(
    user_inputs: List[str],
    measurement_plugins: Dict[str, str]
) -> Union[List[str], None]:
    """Validate the user inputs for measurement plugin indexes.

    Args:
        user_inputs (List[str]): User inputs for measurement plugin indexes.
        measurement_plugins (Dict[str, str]): List of Measurement Plugins.

    Returns:
        Union[List[str], None]: User selected measurement plugins.
    """
    if user_inputs == [ALL_MEAS]:
        user_selected_measurements = list(measurement_plugins.values())
        return user_selected_measurements

    selected_measurements = []
    for plugin_number in user_inputs:
        if plugin_number in measurement_plugins:
            selected_measurements.append(measurement_plugins[plugin_number])

    if len(selected_measurements) == len(user_inputs):
        return selected_measurements

    return None


def get_user_inputs_in_interactive_mode(
    logger: Logger,
    measurement_plugins_base_path: str,
) -> Union[List[str], None]:
    """Get user inputs for measurement package builder in `interactive mode`.

    Args:
        logger (Logger): Logger object.
        measurement_plugins_base_path (str): Measurement plugin base path.

    Returns:
        Union[List[str], None]: User selected measurement infomation.
    """
    measurement_plugins_list = get_folders(measurement_plugins_base_path, logger)

    if not measurement_plugins_list:
        raise FileNotFoundError(
            UserMessages.INVALID_BASE_DIR.format(dir=measurement_plugins_base_path)
        )

    logger.info("\n")
    logger.info(InteractiveModeMessages.AVAILABLE_MEASUREMENTS)
    logger.info("\n")

    measurement_plugins = {}
    for index, measurement_name in enumerate(measurement_plugins_list):
        logger.info(f"{index + 1}.{measurement_name}")
        measurement_plugins[str(index + 1)] = measurement_name

    logger.info("\n")
    user_warning_count = 2

    while user_warning_count > 0:
        user_selected_plugin_numbers = input(
            InteractiveModeMessages.MEASUREMENT_NUMBER.format(
                start=1,
                end=len(measurement_plugins_list)
            )
        ).strip().split(",")

        validated_user_inputs = validate_user_input_for_meas_plugins(
            user_selected_plugin_numbers,
            measurement_plugins,
        )

        if validated_user_inputs:
            return validated_user_inputs

        logger.info(
            InteractiveModeMessages.INVALID_INPUT.format(numbers=user_selected_plugin_numbers)
        )
        user_warning_count -= 1

    return None


def get_user_input_for_upload_packages() -> Tuple[SystemLinkConfig, UploadPackageInfo]:
    """Get user inputs for uploading packages to SystemLink.

    Raises:
        InvalidInputError: If API Key and Feed Name not provided by the user.

    Returns:
        Tuple[SystemLinkConfig, UploadPackageInfo]: SystemLink config credentials and Upload package information. # noqa: W505.
    """
    upload_packages_info = UploadPackageInfo()
    systemlink_config = SystemLinkConfig()

    api_url = input(InteractiveModeMessages.ENTER_API_URL).strip()
    api_key = input(InteractiveModeMessages.ENTER_API_KEY).strip()
    workspace = input(InteractiveModeMessages.ENTER_WORKSPACE.strip())

    if not api_key:
        raise InvalidInputError(UserMessages.NO_API_KEY)
    feed_name = input(InteractiveModeMessages.ENTER_FEED_NAME).strip()

    if not feed_name:
        raise InvalidInputError(InteractiveModeMessages.NO_FEED_NAME)
    overwrite_packages = input(InteractiveModeMessages.OVERWRITE_MEAS).strip().lower() == YES

    upload_packages_info.feed_name = feed_name
    upload_packages_info.overwrite_packages = overwrite_packages

    systemlink_config.api_url = api_url
    systemlink_config.api_key = api_key
    systemlink_config.workspace = workspace

    return systemlink_config, upload_packages_info
