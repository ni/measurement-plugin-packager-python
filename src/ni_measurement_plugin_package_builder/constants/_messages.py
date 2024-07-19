"""NI Measurement Plug-In Package Builder status messages."""


class UserMessages:
    """User Facing console messages."""

    STARTED_EXECUTION = "Starting the NI Measurement Plug-In Package Builder..."
    CHECK_LOG_FILE = "Please check the log file for further details."
    LOG_FILE_LOCATION = "Log File Directory: {log_dir}"
    PROCESS_COMPLETED = "Process Completed."
    VERSION = "Package Version - {version}"
    INVALID_MEAS_DIR = "Invalid measurement plug-in directory - '{dir}'"
    INVALID_BASE_DIR = "Invalid measurement plug-in base directory - '{dir}',\
\nPlease provide the parent directory containing measurement plug-in folders."
    PACKAGE_BUILT = "NI Package for the measurement '{name}' built successfully at '{dir}'"
    NO_TOML_FILE = "The 'pyproject.toml' file is not found in '{dir}'"
    NO_MEAS_FILE = "The 'measurement.py' file is not found in '{dir}'"
    NO_BATCH_FILE = "The 'start.bat' Batch file is not found in '{dir}'"
    SUBPROCESS_ERR = "Command '{cmd}' returned non-zero exit status {returncode}."
    TEMPLATE_FILES_COMPLETED = "Created required components to build NI package for the python\
 measurement plug-in."
    FAILED_PUBLIC_DIR = "Failed to get PublicDocuments directory. Using UserDocuments for Log file."
    FAILED_USER_DIR = "Failed to get UserDocuments directory. Using Temp directory for\
 Log file."
    BUILDING_MEAS = "Building the NI package for the measurement '{name}'..."
    EMPTY_AUTHOR = "No author details provided in 'pyproject.toml' using default author name\
 '{author}'."
    EMPTY_VERSION = "No package version provided in 'pyproject.toml', using default version\
 '{version}'."
    EMPTY_DESCRIPTION = "No package description provided in 'pyproject.toml' using default\
 description '{description}'."
    EMPTY_NAME = "No package name provided in 'pyproject.toml' using default package name\
 '{name}'."
    ACCESS_DENIED = "Access is denied.\
 Please run the tool with Admin privileges or provide a different output directory."
    NO_API_KEY = "No API Key provided. Please provide a valid API key for uploading\
 the measurement packages."
    PACKAGE_UPLOADED = "Measurement package '{package_name}' uploaded to the SystemLink Feed \
'{feed_name}' successfully."
    INVALID_MEAS_PLUGIN = "Invalid measurement plug-in folder, as it is missing one or more of the\
 required files: 'measurement.py', 'start.bat', or 'pyproject.toml'."
    PACKAGE_UPLOAD_FAILED = "Failed to upload the package '{package}' to SystemLink feed '{name}'."
    API_URL_KEY_MISSING = "{key} key found missing in SystemLink Client configuration files."
    FAILED_CLIENT_CREATION = "Failed to instantiate the client for publish packages to SystemLink."


class InteractiveModeMessages:
    """Non interactive mode messages."""

    INTERACTIVE_MODE_ON = "Interactive mode enabled."
    DIR_NOT_REQUIRED = "Interactive mode requires only the '-i' argument, and no other arguments\
 are necessary."
    MEASUREMENT_NUMBER = "Enter measurement plug-in index ({start}-{end}) to build\
 (. to build all): "
    CONTINUE_BUILDING = "Do you want to continue? (y/n): "
    AVAILABLE_MEASUREMENTS = "Available measurements: "
    INVALID_INPUT = "Invalid measurement plug-in indexes {numbers}, please provide valid\
 plug-in indexes."
    UPLOAD_PACKAGE = "Do you want to upload the measurement packages to SystemLink feeds? (y/n): "
    ENTER_API_KEY = "Enter the SystemLink API Key: "
    ENTER_API_URL = "Enter the SystemLink API URL: "
    ENTER_WORKSPACE = "Enter the Workspace Name: "
    ENTER_FEED_NAME = "Enter the Feed Name: "
    SAME_FEED = "Do you want to use same feed? (y/n): "
    NO_FEED_NAME = "No feed name, Please provide a valid feed name for uploading the\
 measurement packages."
    OVERWRITE_MEAS = "Do you want to overwrite the existing measurement packages? (y/n): "
    INPUT_MEAS_PLUGIN_BASE_DIR = "In Interactive mode, User must provide the parent directory\
 containing the measurement plug-in folders.\nEnter the measurement plug-ins parent directory: "
    DEFAULT_SYSTEMLINK_CONFIG = "API URL and Workspace will be fetched from\
 'SystemLink Client' configuration by default."


class NonInteractiveModeMessages:
    """Non interactive mode messages."""

    NON_INTERACTIVE_MODE = "Non-interactive mode enabled"
    INVALID_SELECTED_PLUGINS = "Invalid measurement plug-in name '{input}'\
 provided in '--selected-meas-plugins'.\nPlease enter comma-separated names\
 (Eg: sample_measurement,test_measurement). Or, '.'\
 to build all the available measurements.\nUse interactive mode if the folder name has comma."
    UNWANTED_SYSTEMLINK_CREDENTIALS = "Please provide the argument '-u or --upload-packages' for\
 uploading the packages."
    MEAS_DIR_REQUIRED = "Either '--plugin-dir' or '--base-dir' with '--selected-meas-plugins'\
 arguments are required."
