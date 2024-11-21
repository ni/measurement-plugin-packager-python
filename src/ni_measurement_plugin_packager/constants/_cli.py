"""CLI help Messages."""

DEFAULT_DESCRIPTION = "Python Measurement Plug-In"
DEFAULT_VERSION = "1.0.0"
DEFAULT_AUTHOR = "National Instruments"
YES = "y"


class CliInterface:
    """Command Line Interface Messages."""

    PLUGIN_DIR = "Measurement Plug-in directory."
    PLUGIN_BASE_DIR = "Measurement Plug-ins base directory."
    SELECTED_PLUGINS = "Comma-separated list of measurement plug-ins or\
 dot(.) for building all the available measurements."
    UPLOAD_PACKAGES = "Upload the measurement packages to SystemLink Feed."
    WORK_SPACE = "Name of the workspace to upload the measurement packages."
    API_KEY = "API key of SystemLink server."
    API_URL = "URL of SystemLink API documentation."
    FEED_NAME = "Name of the feed to upload the measurement packages."
    OVERWRITE_PACKAGES = "Overwrite the existing measurement packages in SystemLink feeds."
