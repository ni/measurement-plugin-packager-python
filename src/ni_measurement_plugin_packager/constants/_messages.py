"""Measurement Plug-In Packager status messages."""


class PackagerStatusMessages:
    """Messages describing the status and progress of the Measurement Plug-In Packager."""

    STARTED_EXECUTION = "Initializing the Measurement Plug-In Packager..."
    CHECK_LOG_FILE = "Refer to the log file for detailed information."
    LOG_FILE_LOCATION = "Log File Path: {log_dir}"
    PROCESS_COMPLETED = "Packaging process completed."
    VERSION = "Package Version - {version}"
    INVALID_PLUGIN_DIR = "Invalid measurement plug-in directory - '{dir}'"
    INVALID_PACKAGER_PATH = "Invalid measurement plug-in packager directory."
    INVALID_BASE_DIR = "Invalid base directory for measurement plug-ins: '{dir}'\n\
Provide the parent directory containing measurement plug-in folders."
    PACKAGE_BUILT = "Successfully created NI Package for measurement '{name}' at '{dir}'"
    NO_TOML_FILE = "Missing 'pyproject.toml' in directory: '{dir}'"
    NO_MEASUREMENT_FILE = "Missing 'measurement.py' in directory: '{dir}'"
    NO_BATCH_FILE = "Missing 'start.bat' in directory: '{dir}'"
    SUBPROCESS_ERR = "Command '{cmd}' execution failed with exit status {returncode}."
    TEMPLATE_FILES_COMPLETED = "Generated required template files for NI package creation."
    FAILED_PUBLIC_DIR = (
        "Could not access Public Documents directory. Defaulting to User Documents for logging."
    )
    FAILED_USER_DIR = "Could not access UserDocuments directory. Using Temp directory for logging."
    BUILDING_MEASUREMENT = "Creating NI package for measurement '{name}'..."
    EMPTY_AUTHOR = "No author details found in 'pyproject.toml'. Using default author: '{author}'."
    EMPTY_VERSION = (
        "No package version specified in 'pyproject.toml'. Using default version: '{version}'."
    )
    EMPTY_DESCRIPTION = "No package description provided in 'pyproject.toml'. Using default description: '{description}'."
    EMPTY_NAME = "No package name found in 'pyproject.toml'. Using default package name: '{name}'."
    ACCESS_DENIED = "Permission denied. Run the tool with administrator privileges."
    NO_API_KEY = "Missing API key. Provide a valid key to upload measurement packages."
    PACKAGE_UPLOADED = "Uploaded measurement package '{package_name}' to SystemLink Feed '{feed_name}' successfully."
    INVALID_MEASUREMENT_PLUGIN = "Invalid measurement plug-in folder: missing required files (measurement.py, start.bat, or pyproject.toml)."
    PACKAGE_UPLOAD_FAILED = "Package upload failed: '{package}' to SystemLink feed '{name}'."
    API_URL_KEY_MISSING = "{key} key is missing in SystemLink client configuration files."
    FAILED_CLIENT_CREATION = "Unable to initialize client for publishing packages to SystemLink."


class CommandLinePrompts:
    """Messages guiding user interactions and input requirements for command-line operations."""

    PLUGIN_DIR_REQUIRED = "Specify '--plugin-dir' or '--base-dir' with '--selected-meas-plugins'."
    AVAILABLE_PLUGINS = "Available measurements: "
    INVALID_SELECTED_PLUGINS = "Invalid measurement plug-in name '{input}' provided.\n\
Use comma-separated plugin names (e.g., sample_measurement,test_measurement) or '.' to build all available measurements."
    UNWANTED_SYSTEMLINK_CREDENTIALS = "Use '-u' or '--upload-packages' flag to upload package(s)."
    NO_FEED_NAME = "Missing feed name. Provide a valid feed name for uploading the package(s)."
