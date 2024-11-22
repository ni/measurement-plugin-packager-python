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

    plugins_root: Optional[Path] = None
    plugin_path: Optional[Path] = None
    plugin_names: Optional[str] = None
    upload_packages: bool = False
    systemlink_config: SystemLinkConfig = SystemLinkConfig()
    upload_package_info: UploadPackageInfo = UploadPackageInfo()

    @model_validator(mode="after")
    def validate_measurement_plugin_inputs(self) -> "CliInputs":
        """Validator to validate the measurement plugin inputs."""
        if (
            (
                self.plugin_path
                and any([self.plugins_root, self.plugin_names])
            )
            or (
                all([self.plugins_root, self.plugin_names])
                and self.plugin_path
            )
            or (
                not all([self.plugins_root, self.plugin_names])
                and not self.plugin_path
            )
        ):
            raise FileNotFoundError(CommandLinePrompts.PLUGIN_DIRECTORY_REQUIRED)

        if self.plugins_root and (
            not Path(self.plugins_root).is_dir()
        ):
            raise FileNotFoundError(
                StatusMessages.INVALID_ROOT_DIRECTORY.format(dir=self.plugins_root)
            )

        if self.plugin_path and not Path(self.plugin_path).is_dir():
            raise FileNotFoundError(
                StatusMessages.INVALID_PLUGIN_DIRECTORY.format(dir=self.plugin_path)
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
