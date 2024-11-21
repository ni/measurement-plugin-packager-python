# Measurement Plugin Packager for Python

- [Measurement Plugin Packager for Python](#measurement-plugin-packager-for-python)
  - [Introduction](#introduction)
  - [Dependencies](#dependencies)
  - [Installation](#installation)
  - [Usage](#usage)
    - [1. Non-Interactive Mode](#1-non-interactive-mode)
  - [Notes](#notes)
    - [File Exclusions](#file-exclusions)
    - [SystemLink Upload Requirements](#systemlink-upload-requirements)
    - [Command Line Tips](#command-line-tips)
  - [Additional Resources](#additional-resources)

## Introduction

The NI Measurement Plugin Packager enables users to build Python Measurement Plug-Ins as NI package files (`.nipkg`) and upload them to SystemLink feeds. This tool streamlines the process of package creation and distribution for NI measurement plugins.

## Dependencies

- [Python 3.9](https://www.python.org/downloads/release/python-3913/) or later
- [NI Package Manager 2024 Q4](https://www.ni.com/en/support/downloads/software-products/download.package-manager.html#322516) or later
- NI SystemLink Feeds Manager [1.0.0-dev1](./dependencies/nisystemlink_feeds_manager-1.0.0.dev1-py3-none-any.whl)

## Installation

1. Download the required wheel files from the latest release:
    - `measurement_plugin_packager-X.X.X-py3-none-any.whl`
    - `nisystemlink_feeds_manager-X.X.X-py3-none-any.whl`
2. Install using the command below:

    ```bash
    pip install <path_to_measurement_plugin_packager-X.X.X-py3-none-any.whl> <path_to_nisystemlink_feeds_manager-X.X.X-py3-none-any.whl>
    ```

## Usage

The tool supports two modes of operation:

### 1. Non-Interactive Mode
<!-- TODO: Update the flag names -->
- #### Building Single Plugin

  ```bash
  measurement-plugin-packager --plugin-dir "<measurement_plugin_directory>"
  ```

  What Happens:
  - Creates a `.nipkg` package for the specified measurement plug-in.
  - Package will be saved in: `C:\Users\Public\Documents\NI-Measurement-Plugin-Package-Builder\packages`.
  - Package name will be in the format: `{plugin_name}_{version}_windows_x64.nipkg`

  Example:

  ```bash
  measurement-plugin-packager --plugin-dir "C:/Users/examples/sample_measurement"
  ```

- #### Building Multiple Plugins

  ```bash
  measurement-plugin-packager --base-dir "<measurement_plugin_base_directory>" --selected-meas-plugins "<plugin1,plugin2>"
  ```

  What Happens:
  - Creates `.nipkg` packages for the specified measurement plug-ins.
  - Package will be saved in: `C:\Users\Public\Documents\NI-Measurement-Plugin-Package-Builder\packages`.
  - 
  
  Example:
  
  ```bash
  measurement-plugin-packager --base-dir "C:/Users/examples" --selected-meas-plugins "sample_measurement,test_measurement"
  ```

- #### Uploading Single Plugin to SystemLink

  ```bash
  measurement-plugin-packager --plugin-dir "<measurement_plugin_directory>" --upload-packages --api-url "<systemlink_api_url>" --api-key "<api_key>" --workspace   "<workspace_name>" --feed-name "<feed_name>"
  ```
  
  Example:
  
  ```bash
  measurement-plugin-packager --plugin-dir "C:\Users\examples\sample_measurement" --upload-packages --api-url "https://dev-api.lifecyclesolutions.ni.com/"   --api-key "123234" --workspace "sample_workspace" --feed-name "example_feed"
  ```

- #### Uploading Multiple Plugins to SystemLink

  ```bash
  measurement-plugin-packager --base-dir "<base_directory>" --selected-meas-plugins "<plugin1,plugin2>" --upload-packages --api-url "<systemlink_api_url>"   --api-key "<api_key>" --workspace "<workspace_name>" --feed-name "<feed_name>"
  ```
  
  Example:
  
  ```bash
  measurement-plugin-packager --base-dir "C:\Users\examples" --selected-meas-plugins "sample_measurement,testing_measurement" --upload-packages --api-url "https://  dev-api.lifecyclesolutions.ni.com/" --api-key "123234" --workspace "sample_workspace" --feed-name "example_feed"
  ```

## Notes

### File Exclusions

The following files/directories are automatically ignored during package building:

- `.venv`
- `__pycache__`
- `.cache`
- `dist`
- `.vscode`
- `.vs`
- `.env`
- `poetry.lock`
- `.mypy_cache`
- `.pytest_cache`
- `coverage.xml`

### SystemLink Upload Requirements

- Internet access is required for installing external dependencies.
- When uploading packages:
  - API key and Feed name are mandatory.
  <!-- To be decided -->
  - API URL and Workspace are optional (defaults to SystemLink client configuration if not provided).
- All command-line arguments should be enclosed in double quotes.

### Command Line Tips

- For building multiple plugins, both the base directory and selected measurement plugins must be specified.
- The tool will display the output directory where `.nipkg` files are generated.

## Additional Resources

- [NI Package Builder Documentation](https://www.ni.com/docs/en-US/bundle/package-manager/page/build-package-using-cli.html)
