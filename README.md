# Measurement Plug-In Packager for Python

- [Measurement Plug-In Packager for Python](#measurement-plug-in-packager-for-python)
  - [Introduction](#introduction)
  - [Dependencies](#dependencies)
  - [Installation](#installation)
  - [Usage](#usage)
    - [1. Building Measurement Plug-Ins](#1-building-measurement-plug-ins)
    - [2. Uploading to SystemLink](#2-uploading-to-systemlink)
  - [Directory Utilization](#directory-utilization)
  - [Notes](#notes)
    - [File Exclusions](#file-exclusions)
    - [SystemLink Upload Requirements](#systemlink-upload-requirements)
  - [Additional Resources](#additional-resources)

## Introduction

The NI Measurement Plug-In Packager enables users to build Python measurement plug-ins as NI package files (`.nipkg`) and upload them to SystemLink feeds. This tool streamlines the package creation and distribution process for NI measurement plug-ins.

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

### 1. Building Measurement Plug-Ins
<!-- TODO: Update the flag names -->
- #### Single Plug-In

  ```bash
  measurement-plugin-packager --plugin-dir "<measurement_plugin_directory>"
  ```

  Example:

  ```bash
  measurement-plugin-packager --plugin-dir "C:/Users/examples/sample_measurement"
  ```

- #### Multiple Plug-Ins

  ```bash
  measurement-plugin-packager --base-dir "<measurement_plugin_base_directory>" --selected-meas-plugins "<plugin1,plugin2>"
  ```

  Example:
  
  ```bash
  measurement-plugin-packager --base-dir "C:/Users/examples" --selected-meas-plugins "sample_measurement,test_measurement"
  ```

  Note: The base directory and selected measurement plug-ins must be specified for building multiple measurement plug-ins.

- #### What Happens

  - Creates `.nipkg` package(s) for the specified measurement plug-in(s).
  - Package(s) will be saved in: `C:\Users\Public\Documents\NI-Measurement-Plugin-Package-Builder\packages`.
  - Package name will be in the format: `{plugin_folder_name}_{version}_windows_x64.nipkg` eg: `sample-measurement_0.5.0_windows_x64.nipkg`.

### 2. Uploading to SystemLink

- #### Uploading Single Plug-In to SystemLink

  ```bash
  measurement-plugin-packager --plugin-dir "<measurement_plugin_directory>" --upload-packages --api-url "<systemlink_api_url>" --api-key "<api_key>" --workspace   "<workspace_name>" --feed-name "<feed_name>"
  ```
  
  Example:
  
  ```bash
  measurement-plugin-packager --plugin-dir "C:\Users\examples\sample_measurement" --upload-packages --api-url "https://dev-api.lifecyclesolutions.ni.com/"   --api-key "123234" --workspace "sample_workspace" --feed-name "example_feed"
  ```

- #### Uploading Multiple Plug-Ins to SystemLink

  ```bash
  measurement-plugin-packager --base-dir "<base_directory>" --selected-meas-plugins "<plugin1,plugin2>" --upload-packages --api-url "<systemlink_api_url>"   --api-key "<api_key>" --workspace "<workspace_name>" --feed-name "<feed_name>"
  ```
  
  Example:
  
  ```bash
  measurement-plugin-packager --base-dir "C:\Users\examples" --selected-meas-plugins "sample_measurement,testing_measurement" --upload-packages --api-url "https://  dev-api.lifecyclesolutions.ni.com/" --api-key "123234" --workspace "sample_workspace" --feed-name "example_feed"
  ```

- #### What Happens

  - Builds and saves the `.nipkg` package(s) for the specified measurement plug-in(s).
  - Uploads the package(s) to the specified SystemLink feed.
  
  Note: Use `-o` or `--overwrite` to overwrite an existing package in SystemLink feeds.

## Directory Utilization

- **Base Directory:** `C:\Users\Public\Documents\NI-Measurement-Plugin-Package-Builder`
  - **Packages Directory:** `\packages`
    - Contains the built `.nipkg` files.
  - **Logs Directory:** `\Logs`
  - **Measurement Plug-In(copy) Directory:** `\{plugin_folder_name}`
    - Copies of measurement plug-in folders are stored directly under the base directory.
    - Includes instruction and control files for each measurement plug-in.
  
  Note: If the Public Documents directory is not accessible, it uses your personal Documents directory.

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

- Internet access is required for uploading the package(s).
- When uploading packages:
  - API key and Feed name are mandatory.
  <!-- To be decided -->
  - API URL and Workspace are optional (defaults to SystemLink client configuration if not provided).
- All command-line arguments should be enclosed in double-quotes.

## Additional Resources

- [HLD for the tool.](./docs/ni_package_builder_hld.md)
- [NI Package Builder Documentation.](https://www.ni.com/docs/en-US/bundle/package-manager/page/build-package-using-cli.html)
