"""NI Measurement Plugin Package Builder status messages."""


class UserMessages:
    """User Facing console messages."""

    STARTED_EXECUTION = "Starting the NI Measurement Plugin Package Builder..."
    CHECK_LOG_FILE = "Please check the log file for further details."
    LOG_FILE_LOCATION = "Log File Directory: {log_dir}"
    PROCESS_COMPLETED = "Process Completed."
    VERSION = "Package Version - {version}"
    INTERACTIVE_MODE_ON = "Interactive mode enabled."
    DIR_NOT_REQUIRED = "None of the following options are required for 'Interactive mode':\
 '--plugin-dir', '--base-dir', or '--selected-meas-plugins'."
    MEAS_DIR_REQUIRED = "Either '--plugin-dir' or '--base-dir' with '--selected-meas-plugins'\
 arguments are required."
    NON_INTERACTIVE_MODE = "Non-interactive mode enabled. Provided measurement plugin directory:\
 {dir}"
    INPUT_MEAS_PLUGIN_BASE_DIR = "In Interactive mode, User must provide the parent directory\
 containing the measurement plugin folders.\nEnter the Measurement Plugins parent directory:"
    INVALID_MEAS_DIR = "Invalid measurementlink plugin directory - '{dir}'"
    INVALID_BASE_DIR = "Invalid measurementlink plugin base directory - '{dir}',\
\nPlease provide the parent directory containing measurement plugin folders."
    PACKAGE_BUILT = "NI Package for the measurement '{name}' built successfully at '{dir}'"
    NO_TOML_FILE = "The 'pyproject.toml' file is not found in '{dir}'"
    NO_MEAS_FILE = "The 'measurement.py' file is not found in '{dir}'"
    NO_BATCH_FILE = "The 'start.bat' Batch file is not found in '{dir}'"
    SUBPROCESS_ERR = "Command '{cmd}' returned non-zero exit status {returncode}."
    TEMPLATE_FILES_COMPLETED = "Created required components to build NI package for the python\
 measurement plugin."
    FAILED_PUBLIC_DIR = "Failed to get PublicDocuments directory. Using UserDocuments for Log file."
    FAILED_USER_DIR = "Failed to get UserDocuments directory. Using Temp directory for\
 Log file."
    MEASUREMENT_NUMBER = "Enter Measurement Plugin index number ({start}-{end}) to build\
 [. to build all or Comma separated measurement plugin index numbers Eg: 1,2,3]: "
    CONTINUE_BUILDING = "Do you want to continue building NI Measurement Packages? (y/n): "
    AVAILABLE_MEASUREMENTS = "Available measurements: "
    INVALID_INPUT = "Invalid measurement plugin number."
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
    INVALID_SELECTED_PLUGINS = "Invalid plugin name '{input}' provided in '--selected-meas-plugins'\
.\nPlease enter comma-separated names (Eg: sample_measurement,test_measurement). Or, '.'\
 to build all the available measurements.\nUse interactive mode if the folder name has comma."
    NO_API_KEY = "No API Key, Please Provide an API key for uploading the measurement packages."
    PACKAGE_UPLOADED = "Measurement package '{package_name}' uploaded successfully to the feed \
'{feed_name}' in SystemLink."
    UPLOAD_PACKAGE = "Do you want to upload the measurement packages to systemlink feeds? (y/n): "
    ENTER_API_KEY = "Enter the SystemLink API Key: "
    ENTER_API_URL = "Enter the SystemLink API URL: "
    ENTER_WORKSPACE = "Enter the workspace name: "
    ENTER_FEED_NAME = "Enter the feed name: "
    SAME_FEED = "Do you want to use same feed? (y/n): "
    NO_FEED_NAME = "No feed name, Please provide a valid feed name for uploading the\
 measurement packages."
    OVERWRITE_MEAS = "Do you want to overwrite the existing measurement packages? (y/n): "
    INVALID_MEAS_PLUGIN = "Invalid Measurement Plugin folder, as it is missing one or more of the\
 required files: 'measurement.py', 'start.bat', or 'pyproject.toml'."
