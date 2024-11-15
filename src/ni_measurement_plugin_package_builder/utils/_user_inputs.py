"""Implementation of Command Line Interface."""

from logging import Logger
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ni_measurement_plugin_package_builder.constants import (
    YES,
    InteractiveModeMessages,
    UserMessages,
)
from ni_measurement_plugin_package_builder.models import (
    InvalidInputError,
    SystemLinkConfig,
    UploadPackageInfo,
)
from ni_measurement_plugin_package_builder.utils._helpers import (
    display_available_measurements,
    get_folders,
    get_measurement_plugins,
)

ALL_MEAS = "."


def get_yes_no_response(question: str) -> bool:
    """Get yes or no response from the user.

    Args:
        question (str): Question to be prompted to the user.

    Returns:
        bool: True if user provides yes else False.
    """
    user_input = input(question).strip().lower()
    return user_input == YES


def validate_user_input_for_meas_plugins(
    user_inputs: List[str],
    measurement_plugins: Dict[str, Path],
) -> Optional[List[Path]]:
    """Validate the user inputs for measurement plug-in indexes.

    Args:
        user_inputs (List[str]): User inputs for measurement plug-in indexes.
        measurement_plugins (Dict[str, str]): List of measurement plug-ins.

    Returns:
        Union[List[str], None]: User selected measurement plug-ins.
    """
    if user_inputs == [ALL_MEAS]:
        user_selected_measurements = list(measurement_plugins.values())
        return user_selected_measurements

    selected_measurements = []
    for plugin_number in user_inputs:
        if plugin_number.strip() in measurement_plugins:
            selected_measurements.append(measurement_plugins[plugin_number.strip()])

    if len(selected_measurements) == len(user_inputs):
        return selected_measurements

    return None


def get_user_inputs_in_interactive_mode(
    logger: Logger,
    measurement_plugins_base_path: Path,
) -> Optional[List[Path]]:
    """Get user inputs for measurement package builder in `interactive mode`.

    Args:
        logger (Logger): Logger object.
        measurement_plugins_base_path (str): Measurement plug-in base path.

    Returns:
        Union[List[str], None]: User selected measurement infomation.
    """
    measurement_plugins = get_folders(measurement_plugins_base_path, logger)

    if not measurement_plugins:
        raise FileNotFoundError(
            UserMessages.INVALID_BASE_DIR.format(dir=measurement_plugins_base_path)
        )

    measurement_plugins_with_indexes = get_measurement_plugins(measurement_plugins)
    display_available_measurements(
        logger=logger,
        measurement_plugins=measurement_plugins,
    )
    user_warning_count = 2

    while user_warning_count > 0:
        user_selected_plugin_numbers = (
            input(
                InteractiveModeMessages.MEASUREMENT_NUMBER.format(
                    start=1,
                    end=len(measurement_plugins_with_indexes),
                )
            )
            .strip()
            .split(",")
        )

        validated_user_inputs = validate_user_input_for_meas_plugins(
            user_selected_plugin_numbers,
            measurement_plugins_with_indexes,
        )

        if validated_user_inputs:
            return validated_user_inputs

        logger.info(
            InteractiveModeMessages.INVALID_INPUT.format(numbers=user_selected_plugin_numbers)
        )
        user_warning_count -= 1

    return None


def get_systemlink_config(logger: Logger) -> SystemLinkConfig:
    """Get SystemLink config from the user.

    Args:
        logger (Logger): Logger object.

    Returns:
        SystemLinkConfig: SystemLink config credentials.
    """
    systemlink_config = SystemLinkConfig()

    logger.info(InteractiveModeMessages.DEFAULT_SYSTEMLINK_CONFIG)
    api_url = input(InteractiveModeMessages.ENTER_API_URL).strip()
    api_key = input(InteractiveModeMessages.ENTER_API_KEY).strip()
    workspace = input(InteractiveModeMessages.ENTER_WORKSPACE).strip()

    if not api_key:
        raise InvalidInputError(UserMessages.NO_API_KEY)

    systemlink_config.api_url = api_url
    systemlink_config.api_key = api_key
    systemlink_config.workspace = workspace

    return systemlink_config


def get_feed_name() -> str:
    """Get feed name for uploading packages from the user.

    Raises:
        InvalidInputError: If feed name not provided by the user.

    Returns:
        str: Feed name.
    """
    feed_name = input(InteractiveModeMessages.ENTER_FEED_NAME).strip()

    if not feed_name:
        raise InvalidInputError(InteractiveModeMessages.NO_FEED_NAME)

    return feed_name


def get_upload_package_info() -> UploadPackageInfo:
    """Get upload package information from the user.

    Returns:
        UploadPackageInfo: Upload package information.
    """
    upload_packages_info = UploadPackageInfo()
    feed_name = get_feed_name()
    overwrite_packages = get_yes_no_response(InteractiveModeMessages.OVERWRITE_MEAS)

    upload_packages_info.feed_name = feed_name
    upload_packages_info.overwrite_packages = overwrite_packages

    return upload_packages_info


def get_user_input_for_upload_packages(
    logger: Logger,
) -> Tuple[SystemLinkConfig, UploadPackageInfo]:
    """Get user inputs for uploading packages to SystemLink.

    Args:
        logger (Logger): Logger object.

    Returns:
        Tuple[SystemLinkConfig, UploadPackageInfo]: SystemLink config credentials and Upload package information. # noqa: W505.
    """
    systemlink_config = get_systemlink_config(logger=logger)
    upload_packages_info = get_upload_package_info()

    return systemlink_config, upload_packages_info
