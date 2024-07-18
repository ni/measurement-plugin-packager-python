"""Models for NI Measurement Plugin Package Builder CLI Arguments."""

import os
from typing import Optional

from pydantic import BaseModel, model_validator

from ni_measurement_plugin_package_builder.constants import (
    InteractiveModeMessages,
    NonInteractiveModeMessages,
    UserMessages,
)


class SystemLinkConfig(BaseModel):
    """SystemLink Configuration."""

    api_url: Optional[str] = None
    api_key: Optional[str] = None
    workspace: Optional[str] = None


class UploadPackageInfo(BaseModel):
    """Package information."""

    feed_name: Optional[str] = None
    overwrite_packages: Optional[bool] = False


class CliInputs(BaseModel):
    """Represent Command Line Interface inputs."""

    measurement_plugin_base_path: Optional[str] = None
    measurement_plugin_path: Optional[str] = None
    selected_meas_plugins: Optional[str] = None
    interactive_mode: bool = False
    upload_packages: bool = False
    systemlink_config: Optional[SystemLinkConfig] = None
    upload_package_info: Optional[UploadPackageInfo] = None

    @model_validator(mode="after")
    def validate_non_interactive_mode_inputs(self) -> "CliInputs":
        """Validator to validate the non-interactive mode inputs."""
        if (
            not self.interactive_mode
            and not self.measurement_plugin_path
            and not (self.measurement_plugin_base_path and self.selected_meas_plugins)
        ):
            raise FileNotFoundError(NonInteractiveModeMessages.MEAS_DIR_REQUIRED)

        if self.measurement_plugin_base_path and (
            not os.path.isdir(self.measurement_plugin_base_path)
            or not os.path.exists(self.measurement_plugin_base_path)
        ):
            raise FileNotFoundError(
                UserMessages.INVALID_BASE_DIR.format(dir=self.measurement_plugin_base_path)
            )

        if self.measurement_plugin_path and (
            not os.path.isdir(self.measurement_plugin_path)
            or not os.path.exists(self.measurement_plugin_path)
        ):
            raise FileNotFoundError(
                UserMessages.INVALID_MEAS_DIR.format(dir=self.measurement_plugin_path)
            )

        return self

    @model_validator(mode="after")
    def validate_interactive_mode_inputs(self) -> "CliInputs":
        """Validator to validate the interactive mode inputs."""
        if self.interactive_mode and any(
            [
                self.measurement_plugin_base_path,
                self.measurement_plugin_path,
                self.selected_meas_plugins,
                self.upload_packages,
                self.systemlink_config.api_key,
                self.systemlink_config.api_url,
                self.systemlink_config.workspace,
                self.upload_package_info.overwrite_packages,
                self.upload_package_info.feed_name,
            ]
        ):
            raise FileNotFoundError(InteractiveModeMessages.DIR_NOT_REQUIRED)

        return self

    @model_validator(mode="after")
    def validate_nisystemlink_feeds_manager_inputs(self) -> "CliInputs":
        """Validator to validate the `nisystemlink-feeds-manager` inputs."""
        if not self.upload_packages and any(
            [
                self.systemlink_config.api_key,
                self.systemlink_config.api_url,
                self.systemlink_config.workspace,
            ]
        ):
            raise ValueError(NonInteractiveModeMessages.UNWANTED_SYSTEMLINK_CREDENTIALS)

        if self.upload_packages:
            if not self.systemlink_config.api_key:
                raise ValueError(UserMessages.NO_API_KEY)

            if self.upload_packages and not self.upload_package_info.feed_name:
                raise ValueError(InteractiveModeMessages.NO_FEED_NAME)

        return self
