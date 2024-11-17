# NI Measurement Plugin Python Packager

- [NI Measurement Plugin Python Packager](#ni-measurement-plugin-python-packager)
  - [Overview](#overview)
  - [Prerequisites](#prerequisites)
    - [Software Requirements](#software-requirements)
  - [Installation](#installation)
  - [Usage](#usage)
    - [1. Non-Interactive Mode](#1-non-interactive-mode)
      - [Building Single Plugin](#building-single-plugin)
      - [Building Multiple Plugins](#building-multiple-plugins)
      - [Uploading Single Plugin to SystemLink](#uploading-single-plugin-to-systemlink)
      - [Uploading Multiple Plugins to SystemLink](#uploading-multiple-plugins-to-systemlink)
    - [2. Interactive Mode](#2-interactive-mode)
  - [Notes](#notes)
    - [File Exclusions](#file-exclusions)
    - [SystemLink Upload Requirements](#systemlink-upload-requirements)
  - [Command Line Tips](#command-line-tips)
  - [Additional Resources](#additional-resources)

## Overview

The NI Measurement Plugin Packager enables users to build Python Measurement Plugins as NI package files (`.nipkg`) and upload them to SystemLink feeds. This tool streamlines the process of package creation and distribution for NI measurement plugins.

## Prerequisites

### Software Requirements

- Python 3.9 or higher
- NI Package Manager 2022 Q4 or higher
- NI SystemLink Feeds Manager 1.0.0-dev1 or higher

## Installation

1. Open Command Prompt/Terminal
2. Install the required wheel files:

```bash
pip install <path_to_measurement_plugin_packager-X.X.X-py3-none-any.whl> <path_to_nisystemlink_feeds_manager-X.X.X-py3-none-any.whl>
```

## Usage

The tool supports two modes of operation:

### 1. Non-Interactive Mode

#### Building Single Plugin

```bash
measurement-plugin-packager --plugin-dir "<measurement_plugin_directory>"
```

Example:

```bash
measurement-plugin-packager --plugin-dir "C:/Users/examples/sample_measurement"
```

#### Building Multiple Plugins

```bash
measurement-plugin-packager --base-dir "<measurement_plugin_base_directory>" --selected-meas-plugins "<plugin1,plugin2>"
```

Example:

```bash
measurement-plugin-packager --base-dir "C:/Users/examples" --selected-meas-plugins "sample_measurement,test_measurement"
```

#### Uploading Single Plugin to SystemLink

```bash
measurement-plugin-packager --plugin-dir "<measurement_plugin_directory>" --upload-packages --api-url "<systemlink_api_url>" --api-key "<api_key>" --workspace "<workspace_name>" --feed-name "<feed_name>"
```

Example:

```bash
measurement-plugin-packager --plugin-dir "C:\Users\examples\sample_measurement" --upload-packages --api-url "https://dev-api.lifecyclesolutions.ni.com/" --api-key "123234" --workspace "sample_workspace" --feed-name "example_feed"
```

#### Uploading Multiple Plugins to SystemLink

```bash
measurement-plugin-packager --base-dir "<base_directory>" --selected-meas-plugins "<plugin1,plugin2>" --upload-packages --api-url "<systemlink_api_url>" --api-key "<api_key>" --workspace "<workspace_name>" --feed-name "<feed_name>"
```

Example:

```bash
measurement-plugin-packager --base-dir "C:\Users\examples" --selected-meas-plugins "sample_measurement,testing_measurement" --upload-packages --api-url "https://dev-api.lifecyclesolutions.ni.com/" --api-key "123234" --workspace "sample_workspace" --feed-name "example_feed"
```

### 2. Interactive Mode

Start the interactive mode with:

```bash
measurement-plugin-packager -i
```

Follow the prompts to input required information for building and uploading packages.

<!-- TODO: Include example screenshots -->

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

## Command Line Tips

- For building multiple plugins, both the base directory and selected measurement plugins must be specified.
- The tool will display the output directory where `.nipkg` files are generated.
- Use the interactive mode (-i) for a guided experience through the build and upload process.

## Additional Resources

- [NI Package Builder Documentation](https://www.ni.com/docs/en-US/bundle/package-manager/page/build-package-using-cli.html)
