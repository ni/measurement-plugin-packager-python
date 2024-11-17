"""Initialize the models."""

# flake8: noqa

from measurement_plugin_packager.models._cli import (
    CliInputs,
    SystemLinkConfig,
    UploadPackageInfo,
)
from measurement_plugin_packager.models._exceptions import InvalidInputError
from measurement_plugin_packager.models._package_info import PackageInfo
