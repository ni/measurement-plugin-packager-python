"""Models for NI Measurement Plugin Package Builder CLI Arguments."""

import os
from typing import Optional

from pydantic import BaseModel, model_validator

from ni_measurement_plugin_package_builder.constants import UserMessages


class UploadPackageInputs(BaseModel):
    """Upload package user inputs."""

    api_url: Optional[str] = None
    api_key: Optional[str] = None
    workspace: Optional[str] = None
    feed_name: Optional[str] = None
    overwrite_packages: Optional[bool] = False


class CliInputs(BaseModel):
    """Represent Command Line Interface inputs."""

    measurement_plugin_base_path: Optional[str] = None
    measurement_plugin_path: Optional[str] = None
    selected_meas_plugins: Optional[str] = None
    interactive_mode: Optional[bool] = False
    upload_packages: Optional[bool] = False
    upload_packages_info: Optional[UploadPackageInputs]

    @model_validator(mode="after")
    def validate_cli_inputs(self) -> "CliInputs":
        """Validator to validate the CLI inputs.

        Returns:
            CliInputs: Validated CLI inputs.
        """
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

        if (
            self.measurement_plugin_base_path
            and not self.interactive_mode
            and not self.selected_meas_plugins
        ):
            raise FileNotFoundError(UserMessages.INVALID_SELECTED_PLUGINS)

        return self
