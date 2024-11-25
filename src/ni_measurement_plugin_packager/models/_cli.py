"""Models for Measurement Plug-In Packager CLI Arguments."""

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, model_validator

from ni_measurement_plugin_packager.constants import CommandLinePrompts, StatusMessages


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

    base_input_dir: Optional[Path] = None
    input_path: Optional[Path] = None
    plugin_dir_names: Optional[str] = None
    upload_packages: bool = False
    systemlink_config: SystemLinkConfig = SystemLinkConfig()
    upload_package_info: UploadPackageInfo = UploadPackageInfo()

    @model_validator(mode="after")
    def validate_measurement_plugin_inputs(self) -> "CliInputs":
        """Validator to validate the measurement plugin inputs."""
        if (
            (self.input_path and any([self.base_input_dir, self.plugin_dir_names]))
            or (all([self.base_input_dir, self.plugin_dir_names]) and self.input_path)
            or (not all([self.base_input_dir, self.plugin_dir_names]) and not self.input_path)
        ):
            raise FileNotFoundError(CommandLinePrompts.PLUGIN_DIRECTORY_REQUIRED)

        if self.base_input_dir and (not Path(self.base_input_dir).is_dir()):
            raise FileNotFoundError(
                StatusMessages.INVALID_ROOT_DIRECTORY.format(dir=self.base_input_dir)
            )

        if self.input_path and not Path(self.input_path).is_dir():
            raise FileNotFoundError(
                StatusMessages.INVALID_PLUGIN_DIRECTORY.format(dir=self.input_path)
            )

        return self

    @model_validator(mode="after")
    def validate_systemlink_inputs(self) -> "CliInputs":
        """Validator to validate the SystemLink related inputs."""
        if not self.upload_packages and any(
            [
                self.systemlink_config.api_key,
                self.systemlink_config.api_url,
                self.systemlink_config.workspace,
            ]
        ):
            raise ValueError(CommandLinePrompts.UNWANTED_SYSTEMLINK_CREDENTIALS)

        if self.upload_packages:
            if not self.systemlink_config.api_key:
                raise ValueError(StatusMessages.API_KEY_MISSING)

            if not self.upload_package_info.feed_name:
                raise ValueError(CommandLinePrompts.NO_FEED_NAME)

        return self
