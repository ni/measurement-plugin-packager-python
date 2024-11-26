# Measurement Plug-In Packager for Python

- [Measurement Plug-In Packager for Python](#measurement-plug-in-packager-for-python)
  - [Introduction](#introduction)
  - [Dependencies](#dependencies)
  - [Installation](#installation)
  - [Usage](#usage)
    - [1. Packaging a Single Measurement Plug-in](#1-packaging-a-single-measurement-plug-in)
    - [2. Packaging Multiple Measurement Plug-ins](#2-packaging-multiple-measurement-plug-ins)
    - [3. Packaging and Publishing the Measurement Plug-in](#3-packaging-and-publishing-the-measurement-plug-in)
  - [Notes](#notes)
    - [File Exclusions](#file-exclusions)
  - [Additional Resources](#additional-resources)

## Introduction

The Measurement Plug-In Packager enables users to build Python measurement plug-ins as NI package
files (`.nipkg`) and upload them to SystemLink feeds. This tool streamlines the process of building
and distributing measurement plug-ins efficiently.

## Dependencies

- [Python 3.9](https://www.python.org/downloads/release/python-3913/) or later
- [NI Package Manager 2024
  Q4](https://www.ni.com/en/support/downloads/software-products/download.package-manager.html#322516)
  or later
- [NI SystemLink Client 2024
  Q1](https://www.ni.com/en/support/downloads/software-products/download.systemlink-client.html#521644)
  or later
- NI SystemLink Feeds Manager
  [1.0.0-dev1](./dependencies/nisystemlink_feeds_manager-1.0.0.dev1-py3-none-any.whl)

## Installation

1. Download the required wheel files from the latest release:
    - `ni_measurement_plugin_packager-X.X.X-py3-none-any.whl`
    - `nisystemlink_feeds_manager-X.X.X-py3-none-any.whl`
2. Use the following command to install:

    ```bash
    pip install <path_to_ni_measurement_plugin_packager-X.X.X-py3-none-any.whl> <path_to_nisystemlink_feeds_manager-X.X.X-py3-none-any.whl>
    ```

## Usage

### 1. Packaging a Single Measurement Plug-in

The following command takes in `--input-path` specifying the measurement plug-in directory path to
build the `.nipkg` file. The package is created at `<Public
Documents>\NI-Measurement-Plugin-Packager\packages`.

The package is named in this format:
`{plugin_folder_name}_{version}_windows_x64.nipkg`. Example:
`sample_measurement_0.5.0_windows_x64.nipkg` where the version is picked from the respective
measurement plug-in's measurement.py file.

  ```bash
  measurement-plugin-packager --input-path "<measurement_plugin_directory>"
  ```

  Example:

  ```bash
  measurement-plugin-packager --input-path "C:/Users/examples/sample_measurement"
  ```

  **Note:**
  
  If the Public Documents directory is inaccessible, the tool defaults to the "Documents" directory.
  In this location, `.nipkg` files are saved in the `\packages` folder, log files are saved in the
  `\Logs` folder and the packaged measurement plug-in folder is copied to the
  `\{plugin_folder_name}` subdirectory.
  
### 2. Packaging Multiple Measurement Plug-ins

You can package multiple measurement plug-ins from a parent directory by specifying plug-in(s)
directory name. Use the following command with `--base-input-dir`, and `--plugin-dir-name` to build
`.nipkg` packages for the specified measurement plug-in(s) from the base directory.

  ```bash
  measurement-plugin-packager --base-input-dir "<measurement_plugin_base_directory>" --plugin-dir-name "<plugin1,plugin2>"
  ```

  Example:
  
  ```bash
  measurement-plugin-packager --base-input-dir "C:/Users/examples" --plugin-dir-name "sample_measurement,test_measurement"
  ```

### 3. Packaging and Publishing the Measurement Plug-in

**Prerequisites:**

- [SystemLink Client Setup on the PC](https://www.ni.com/docs/en-US/bundle/systemlink-enterprise/page/setting-up-systemlink-client.html).
- Active internet connection.
- Command-line arguments should be enclosed in double-quotes.
  
To publish measurement plug-in packages directly to the SystemLink, in addition to the measurement plug-in directory path, you must provide the following values,

- SystemLink API URL (`--api-url`)
- API Key (`--api-key`)
- Workspace name (`--workspace`)
- Feed name (`--feed-name`)

```bash
measurement-plugin-packager --input-path "<measurement_plugin_directory>" --upload-packages --api-url "<systemlink_api_url>" --api-key "<api_key>" --workspace "<workspace_name>" --feed-name "<feed_name>"
```

Example:

```bash
measurement-plugin-packager --input-path "C:\Users\examples\sample_measurement" --upload-packages --api-url "https://api.example.com/" --api-key "123abc" --workspace "your-workspace" --feed-name "your-feed-name"
```

Similarly, to publish multiple measurement plug-ins, replace `--input-path` with `--base-input-dir` and specify
`--plugin-dir-name` as shown below.

Example:

```bash
measurement-plugin-packager --base-input-dir "C:/Users/examples" --plugin-dir-name "sample_measurement,test_measurement" --upload-packages --api-url "https://api.example.com/" --api-key "123abc" --workspace "your-workspace" --feed-name "your-feed-name"
```

**Note:**

- Use `-o` or `--overwrite` to replace an existing package in SystemLink feeds.
- The tool doesn't publish any existing packages. Only packages built during the current packaging process can be published.
  
## Notes

### File Exclusions

The following files and directories are ignored while packaging:

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

## Additional Resources

- [NI Package Builder
  Documentation](https://www.ni.com/docs/en-US/bundle/package-manager/page/build-package-using-cli.html)
