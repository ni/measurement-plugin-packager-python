# Measurement Plug-In Packager for Python

- [Measurement Plug-In Packager for Python](#measurement-plug-in-packager-for-python)
  - [Introduction](#introduction)
  - [Dependencies](#dependencies)
  - [Installation](#installation)
  - [Usage](#usage)
    - [1. Building Measurement Plug-In Packages](#1-building-measurement-plug-in-packages)
    - [2. Building and Uploading Measurement Plug-In Packages to SystemLink](#2-building-and-uploading-measurement-plug-in-packages-to-systemlink)
  - [Directory Utilization](#directory-utilization)
  - [Notes](#notes)
    - [File Exclusions](#file-exclusions)
    - [Requirements to upload packages to SystemLink](#requirements-to-upload-packages-to-systemlink)
  - [Additional Resources](#additional-resources)

## Introduction

The Measurement Plug-In Packager enables users to build Python measurement plug-ins as NI package files (`.nipkg`) and upload them to SystemLink feeds. This tool streamlines the process of building and distributing measurement plug-ins efficiently.

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

### 1. Building Measurement Plug-In Packages

- #### What Happens

  - Creates `.nipkg` package(s) for the specified measurement plug-in(s).
  - Package(s) will be created under: `C:\Users\Public\Documents\NI-Measurement-Plugin-Packager\packages`.
  - Package name will be in the format: `{plugin_folder_name}_{version}_windows_x64.nipkg` eg: `sample-measurement_0.5.0_windows_x64.nipkg`.

- #### Single Plug-in

  ```bash
  measurement-plugin-packager --input-path "<measurement_plugin_directory>"
  ```

  Example:

  ```bash
  measurement-plugin-packager --input-path "C:/Users/examples/sample_measurement"
  ```

- #### Multiple Plug-ins

  ```bash
  measurement-plugin-packager --base-input-dir "<measurement_plugin_base_directory>" --plugin-dir-name "<plugin1,plugin2>"
  ```

  Example:
  
  ```bash
  measurement-plugin-packager --base-input-dir "C:/Users/examples" --plugin-dir-name "sample_measurement,test_measurement"
  ```

  Note: The base input directory and plug-ins directory name must be specified for building multiple measurement plug-ins.

### 2. Building and Uploading Measurement Plug-In Packages to SystemLink

- #### What Happens

  - Builds and saves the `.nipkg` package(s) for the specified measurement plug-in(s).
  - Uploads the package(s) to the specified SystemLink feed.
  
  Note: Use `-o` or `--overwrite` to overwrite an existing package in SystemLink feeds.

- #### Uploading Single Plug-In to SystemLink

  ```bash
  measurement-plugin-packager --input-path "<measurement_plugin_directory>" --upload-packages --api-url "<systemlink_api_url>" --api-key "<api_key>" --workspace   "<workspace_name>" --feed-name "<feed_name>"
  ```
  
  Example:
  
  ```bash
  measurement-plugin-packager --input-path "C:\Users\examples\sample_measurement" --upload-packages --api-url "https://dev-api.lifecyclesolutions.ni.com/"   --api-key "123234" --workspace "sample_workspace" --feed-name "example_feed"
  ```

- #### Uploading Multiple Plug-Ins to SystemLink

  ```bash
  measurement-plugin-packager --base-input-dir "<base_directory>" --plugin-dir-name "<plugin1,plugin2>" --upload-packages --api-url "<systemlink_api_url>"   --api-key "<api_key>" --workspace "<workspace_name>" --feed-name "<feed_name>"
  ```
  
  Example:
  
  ```bash
  measurement-plugin-packager --base-input-dir "C:\Users\examples" --plugin-dir-name "sample_measurement,testing_measurement" --upload-packages --api-url "https://  dev-api.lifecyclesolutions.ni.com/" --api-key "123234" --workspace "sample_workspace" --feed-name "example_feed"
  ```

## Directory Utilization

- **Base Directory:** `C:\Users\Public\Documents\NI-Measurement-Plugin-Packager`
  - **Packages Directory:** `\packages`
    - Contains the built `.nipkg` files.
  - **Logs Directory:** `\Logs`
  - **Measurement Plug-In(copy) Directory:** `\{plugin_folder_name}`
    - Copies of measurement plug-in folders are stored directly under the base directory.
    - Includes instruction and control files for each measurement plug-in.
  
  Note: If the Public Documents directory is not accessible, this tool uses your personal Documents directory.

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

### Requirements to upload packages to SystemLink

- Internet access is required for uploading the package(s).
- When uploading package(s):
  - API key, API URL, Workspace, and Feed name are mandatory.
- All command-line arguments should be enclosed in double-quotes.

## Additional Resources

- [NI Package Builder Documentation.](https://www.ni.com/docs/en-US/bundle/package-manager/page/build-package-using-cli.html)
