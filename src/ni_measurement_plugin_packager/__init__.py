"""Implementation of Measurement Plug-In Package Builder."""

__version__ = "1.3.0-dev3"

import subprocess  # nosec: B404
from pathlib import Path
from typing import Optional

import click
from nisystemlink_feeds_manager.clients.core import ApiException
from pydantic import ValidationError

from ni_measurement_plugin_packager._support._helpers import (
    build_package,
    get_publish_package_client,
    publish_package_to_systemlink,
    is_valid_folder,
)
from ni_measurement_plugin_packager._support._interactive_mode import (
    publish_packages_in_interactive_mode,
)
from ni_measurement_plugin_packager._support._logger import (
    initialize_logger,
    remove_handlers,
    setup_logger_with_file_handler,
)
from ni_measurement_plugin_packager._support._non_interactive_mode import (
    publish_packages_in_non_interactive_mode,
)
from ni_measurement_plugin_packager.constants import (
    CliInterface,
    InteractiveModeMessages,
    NonInteractiveModeMessages,
    UserMessages,
)
from ni_measurement_plugin_packager.models import (
    CliInputs,
    SystemLinkConfig,
    UploadPackageInfo,
)

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option("-i", "--interactive-mode", is_flag=True, help=CliInterface.INTERACTIVE_BUILDER)
@click.option(
    "-p",
    "--plugin-dir",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    required=False,
    help=CliInterface.MLINK_DIR,
)
@click.option(
    "-b",
    "--base-dir",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    required=False,
    help=CliInterface.MLINK_BASE_DIR,
)
@click.option(
    "-s",
    "--selected-plugins",
    default="",
    required=False,
    help=CliInterface.SELECTED_PLUGINS,
)
@click.option("-u", "--upload-packages", is_flag=True, help=CliInterface.UPLOAD_PACKAGES)
@click.option("-a", "--api-url", default=None, required=False, help=CliInterface.API_URL)
@click.option("-k", "--api-key", default=None, required=False, help=CliInterface.API_KEY)
@click.option("-w", "--workspace", default=None, required=False, help=CliInterface.WORK_SPACE)
@click.option("-f", "--feed-name", default=None, required=False, help=CliInterface.FEED_NAME)
@click.option("-o", "--overwrite", is_flag=True, help=CliInterface.OVERWRITE_PACKAGES)
def run(
    interactive_mode: bool,
    plugin_dir: Optional[Path],
    base_dir: Optional[Path],
    selected_plugins: Optional[str],
    upload_packages: bool,
    api_url: Optional[str],
    api_key: Optional[str],
    workspace: Optional[str],
    feed_name: Optional[str],
    overwrite: Optional[bool],
) -> None:
    """Create and upload package files for Python measurement plug-ins to SystemLink Feeds."""
    try:
        logger = initialize_logger(name="console_logger")
        logger.info(UserMessages.STARTED_EXECUTION)

        systemlink_config = SystemLinkConfig(api_key=api_key, api_url=api_url, workspace=workspace)
        upload_package_info = UploadPackageInfo(feed_name=feed_name, overwrite_packages=overwrite)
        interactive_mode_input_parent_dir: Optional[Path] = None

        cli_args = CliInputs(
            measurement_plugin_base_path=base_dir,
            interactive_mode=interactive_mode,
            measurement_plugin_path=plugin_dir,
            upload_packages=upload_packages,
            selected_plugins=selected_plugins,
            systemlink_config=systemlink_config,
            upload_package_info=upload_package_info,
        )

        if interactive_mode:
            interactive_mode_input_parent_dir = Path(
                input(InteractiveModeMessages.INPUT_MEAS_PLUGIN_BASE_DIR).strip()
            )
            if not is_valid_folder(interactive_mode_input_parent_dir):
                raise FileNotFoundError(
                    UserMessages.INVALID_BASE_DIR.format(dir=interactive_mode_input_parent_dir)
                )

        remove_handlers(logger)
        logger = initialize_logger(name="debug_logger")
        output_path: Path
        if cli_args.measurement_plugin_base_path:
            output_path = cli_args.measurement_plugin_base_path
        elif cli_args.measurement_plugin_path:
            output_path = cli_args.measurement_plugin_path
        elif interactive_mode_input_parent_dir:
            output_path = interactive_mode_input_parent_dir
        logger, log_folder_path = setup_logger_with_file_handler(
            output_path,
            logger=logger,
        )
        logger.debug(UserMessages.VERSION.format(version=__version__))
        logger.info(UserMessages.LOG_FILE_LOCATION.format(log_dir=log_folder_path))

        if interactive_mode_input_parent_dir and interactive_mode:
            logger.debug(InteractiveModeMessages.INTERACTIVE_MODE_ON)
            publish_packages_in_interactive_mode(
                logger=logger,
                measurement_plugin_base_path=interactive_mode_input_parent_dir,
            )
        else:
            logger.debug(NonInteractiveModeMessages.NON_INTERACTIVE_MODE)
            publish_package_client = None
            if upload_packages:
                publish_package_client = get_publish_package_client(
                    logger=logger,
                    systemlink_config=systemlink_config,
                )

            if cli_args.measurement_plugin_base_path and cli_args.selected_plugins:
                publish_packages_in_non_interactive_mode(
                    logger=logger,
                    measurement_plugin_base_path=cli_args.measurement_plugin_base_path,
                    selected_plugins=cli_args.selected_plugins,
                    publish_package_client=publish_package_client,
                    upload_package_info=upload_package_info,
                )

            if cli_args.measurement_plugin_path:
                package_path = build_package(
                    logger=logger,
                    measurement_plugin_path=cli_args.measurement_plugin_path,
                )
                if publish_package_client and package_path:
                    upload_response = publish_package_to_systemlink(
                        package_path=package_path,
                        publish_package_client=publish_package_client,
                        upload_package_info=upload_package_info,
                    )
                    logger.info(
                        UserMessages.PACKAGE_UPLOADED.format(
                            package_name=upload_response.file_name,
                            feed_name=upload_package_info.feed_name,
                        )
                    )
                logger.info("")

    except ApiException as ex:
        measurement_plugin = Path(str(cli_args.measurement_plugin_path)).name
        logger.debug(ex, exc_info=True)
        logger.info(
            UserMessages.PACKAGE_UPLOAD_FAILED.format(
                package=measurement_plugin,
                name=upload_package_info.feed_name,
            )
        )
        logger.info(ex.error.message)
        logger.info(UserMessages.CHECK_LOG_FILE)

    except PermissionError as error:
        logger.info(UserMessages.ACCESS_DENIED)
        logger.debug(error, exc_info=True)

    except subprocess.CalledProcessError as ex:
        logger.debug(ex, exc_info=True)
        logger.info(UserMessages.SUBPROCESS_ERR.format(cmd=ex.cmd, returncode=ex.returncode))
        logger.info(UserMessages.CHECK_LOG_FILE)

    except (FileNotFoundError, KeyError, ValidationError) as ex:
        logger.debug(ex, exc_info=True)
        logger.info(ex)
        logger.info(UserMessages.CHECK_LOG_FILE)

    except Exception as ex:
        logger.debug(ex, exc_info=True)
        logger.info(ex)
        logger.info(UserMessages.CHECK_LOG_FILE)

    finally:
        logger.info(UserMessages.PROCESS_COMPLETED)