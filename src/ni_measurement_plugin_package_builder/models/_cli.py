"""Models for NI Measurement Plugin Package Builder CLI Arguments."""

import os
from typing import Optional

from pydantic import BaseModel, model_validator, ValidationError

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
    interactive_mode: Optional[bool] = False
    upload_packages: Optional[bool] = False
    systemlink_config: Optional[SystemLinkConfig] = SystemLinkConfig()
    upload_package_info: Optional[UploadPackageInfo] = UploadPackageInfo()

    @model_validator(mode="after")
    def validate_non_interactive_mode_inputs(self) -> "CliInputs":
        """Validator to validate the non-interactive mode inputs.

        Returns:
            CliInputs: Validated non-interactive mode inputs.
        """
        if self.measurement_plugin_base_path and (
            not os.path.isdir(self.measurement_plugin_base_path)
            or not os.path.exists(self.measurement_plugin_base_path)
        ):
            raise ValidationError(
                UserMessages.INVALID_BASE_DIR.format(dir=self.measurement_plugin_base_path)
            )

        if self.measurement_plugin_path and (
            not os.path.isdir(self.measurement_plugin_path)
            or not os.path.exists(self.measurement_plugin_path)
        ):
            raise ValidationError(
                UserMessages.INVALID_MEAS_DIR.format(dir=self.measurement_plugin_path)
            )

        if (
            not self.interactive_mode and
            not self.measurement_plugin_path and
            not (self.measurement_plugin_base_path and self.selected_meas_plugins)
        ):
            raise ValidationError(NonInteractiveModeMessages.MEAS_DIR_REQUIRED)

        return self

    @model_validator(mode="after")
    def validate_interactive_mode_inputs(self) -> "CliInputs":
        """Validator to validate the interactive mode inputs.

        Returns:
            CliInputs: Validated interactive mode inputs.
        """
        if self.interactive_mode and any(
            [
                self.measurement_plugin_base_path,
                self.measurement_plugin_path,
                self.selected_meas_plugins
            ]
        ):
            raise ValidationError(InteractiveModeMessages.DIR_NOT_REQUIRED)

        return self

    @model_validator(mode="after")
    def validate_nisystemlink_feeds_manager_inputs(self) -> "CliInputs":
        """Validator to validate the `nisystemlink-feeds-manager` inputs.

        Returns:
            CliInputs: Validated nisystemlink feeds manager inputs.
        """
        if not self.upload_packages and any(
            [
                self.systemlink_config.api_key,
                self.systemlink_config.api_url,
                self.systemlink_config.workspace
            ]
        ):
            raise ValidationError(NonInteractiveModeMessages.UNWANTED_SYSTEMLINK_CREDENTIALS)

        if self.upload_packages and not self.systemlink_config.api_key:
            raise ValidationError(UserMessages.NO_API_KEY)

        if self.upload_packages and not self.upload_package_info.feed_name:
            raise ValidationError(InteractiveModeMessages.NO_FEED_NAME)

        return self
