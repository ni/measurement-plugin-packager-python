# NI Measurement Plugin Package builder

## Description

NI Measurement Plugin Package builder enables user to build Python Measurement plugins as NI package files.

## Prerequistes

- Python (3.8 and above)
- NI Package manager

## Code Setup

- Clone the repository using `git clone <respository link>`.
- Check out to the required branch using `git checkout <branch name>`.

## Setup Virtual Environment

- Open terminal.
- Run `cd ni_measurement_plugin_package_builder`
- Run `poetry env use <py3.8.exe path>`.
- Run `poetry shell` to activate virtual environment.
- Run `pip install ..\dependencies\nisystemlink_feeds_manager-X.X.X-py3-none-any.whl`.
- Run `poetry install` to install dependency files.

## Build whl File

- Run `poetry build` to build whl file.

## How to run?

- Open terminal.
- There are two ways in which user can build packages,
    1. Non-interactive mode
    2. Interactive mode

### Non-interactive mode
- To build a single measurement plugin, run the following command
    `ni-measurement-plugin-package-builder --plugin-dir <measurement_plugin_directory>`
    Example: `ni-measurement-plugin-package-builder --plugin-dir "C:\Users\examples\sample_measurement"`
- To build multiple measurement plugins, run the following command
    `ni-measurement-plugin-package-builder --base-dir <measurement_plugin_base_directory> --selected-meas-plugins <list_of_comma_separated_meas_plugins>`
    Example: `ni-measurement-plugin-package-builder --base-dir "C:\Users\examples" --selected-meas-plugins "sample_measurement,testing_measurement"`
- To upload the single measurement package to systemlink, run the following command
    `ni-measurement-plugin-package-builder --plugin-dir <measurement_plugin_directory> --upload-packages --api-url <systemlink_api_url> --api-key <systemlink_api_key> --workspace <workspace_name> --feed-name <name_of_the_feed>`
    Example: `ni-measurement-plugin-package-builder --plugin-dir "C:\Users\examples\sample_measurement" --upload-packages --api-url "https://dev-api.lifecyclesolutions.ni.com/" --api-key "123234" --workspace "sample_workspace" --feed-name "example_feed"`
- To upload the multiple measurement packages to systemlink, run the following command
    `ni-measurement-plugin-package-builder --base-dir <measurement_plugin_base_directory> --selected-meas-plugins <list_of_comma_separated_meas_plugins> --upload-packages --api-url <systemlink_api_url> --api-key <systemlink_api_key> --workspace <workspace_name> --feed-name <name_of_the_feed>`
    Example: `ni-measurement-plugin-package-builder --base-dir "C:\Users\examples" --selected-meas-plugins "sample_measurement,testing_measurement" --upload-packages --api-url "https://dev-api.lifecyclesolutions.ni.com/" --api-key "123234" --workspace "sample_workspace" --feed-name "example_feed"`
- Input arguments should be provided within double quotes.
- For uploading the packages, if the `api-url` and `workspace` not provided then the SystemLink client configuration will be utilized.

### Interactive mode
- To build multiple measurement plugins, the parent directory containing the measurement plugin folders must be provided
- To start the tool in interactive mode, run the following command
    `ni-measurement-plugin-package-builder -i`

## Note

- Require Internet access to install the external dependencies of NI Measurement Plugin Package builder.

## Reference Link

- [NI package builder](https://www.ni.com/docs/en-US/bundle/package-manager/page/build-package-using-cli.html)