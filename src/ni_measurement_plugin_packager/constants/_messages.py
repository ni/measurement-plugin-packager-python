"""Measurement Plug-In Packager status messages."""


class StatusMessages:
    """Messages describing the status and progress of the Measurement Plug-In Packager."""

    STARTED_EXECUTION = "Initializing the Measurement Plug-In Packager..."
    CHECK_LOG_FILE = "Refer to the log file for detailed information."
    LOG_FILE_PATH = "Log File Path: {log_dir}"
    COMPLETION = "Packaging process completed."
    PACKAGE_VERSION = "Package Version - {version}"
    INVALID_PLUGIN_DIRECTORY = "Invalid measurement plug-in directory - '{dir}'"
    INVALID_PACKAGER_PATH = "Invalid measurement plug-in packager directory."
    INVALID_ROOT_DIRECTORY = "Invalid root directory for measurement plug-ins: '{dir}'\n\
Provide the parent directory containing measurement plug-in folders."
    PACKAGE_BUILT = "Successfully created NI Package for measurement '{name}' at '{dir}'"
    MISSING_TOML_FILE = "Missing 'pyproject.toml' in directory: '{dir}'"
    MISSING_MEASUREMENT_FILE = "Missing 'measurement.py' in directory: '{dir}'"
    MISSING_BATCH_FILE = "Missing 'start.bat' in directory: '{dir}'"
    SUBPROCESS_ERROR = "Command '{cmd}' execution failed with exit status {returncode}."
    TEMPLATE_FILES_GENERATED = "Generated required template files for NI package creation."
    PUBLIC_DIRECTORY_INACCESSIBLE = (
        "Could not access Public Documents directory. Defaulting to User Documents for logging."
    )
    USER_DIRECTORY_INACCESSIBLE = "Could not access UserDocuments directory. Using Temp directory for logging."
    BUILDING_PACKAGE = "Creating NI package for measurement '{name}'..."
    NO_AUTHOR = "No author details found in 'pyproject.toml'. Using default author: '{author}'."
    NO_VERSION = (
        "No package version specified in 'pyproject.toml'. Using default version: '{version}'."
    )
    NO_DESCRIPTION = "No package description provided in 'pyproject.toml'. Using default description: '{description}'."
    NO_NAME = "No package name found in 'pyproject.toml'. Using default package name: '{name}'."
    ACCESS_DENIED = "Permission denied. Run the tool with administrator privileges."
    API_KEY_MISSING = "Missing API key. Provide a valid key to upload measurement packages."
    PACKAGE_UPLOADED = "Uploaded measurement package '{package_name}' to SystemLink Feed '{feed_name}' successfully."
    INVALID_PLUGIN = "Invalid measurement plug-in folder: missing required files (measurement.py, start.bat, or pyproject.toml)."
    UPLOAD_FAILED = "Package upload failed: '{package}' to SystemLink feed '{name}'."
    API_URL_KEY_MISSING = "{key} key is missing in SystemLink client configuration files."
    CLIENT_CREATION_FAILED = "Unable to initialize client for publishing packages to SystemLink."


class CommandLinePrompts:
    """Messages guiding user interactions and input requirements for command-line operations."""

    PLUGIN_DIRECTORY_REQUIRED = "Specify '--plugin-path' or '--plugins-root' with '--plugin-names'."
    AVAILABLE_PLUGINS = "Available measurements: "
    SELECTED_PLUGINS_INVALID = "Invalid measurement plug-in name '{input}' provided.\n\
Use comma-separated plugin names (e.g., sample_measurement,test_measurement) or '.' to build all available measurements."
    UNWANTED_SYSTEMLINK_CREDENTIALS = "Use '-u' or '--upload-packages' flag to upload package(s)."
    NO_FEED_NAME = "Missing feed name. Provide a valid feed name for uploading the package(s)."
