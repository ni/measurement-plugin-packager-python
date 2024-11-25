"""Implementation of Measurement Plug-In Packager."""

__version__ = "1.3.0-dev3"

import subprocess  # nosec: B404
from pathlib import Path
from typing import Optional

import click
from nisystemlink_feeds_manager.clients.core import ApiException
from pydantic import ValidationError

from ni_measurement_plugin_packager._support._helpers import (
    build_package,
    initialize_systemlink_client,
    process_and_upload_packages,
    upload_to_systemlink_feed,
)
from ni_measurement_plugin_packager._support._logger import (
    initialize_logger,
    remove_handlers,
    setup_logger_with_file_handler,
)
from ni_measurement_plugin_packager.constants import CommandLinePrompts, StatusMessages
from ni_measurement_plugin_packager.models import (
    CliInputs,
    SystemLinkConfig,
    UploadPackageInfo,
)

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "-p",
    "--input-path",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    required=False,
    help="Specify the directory containing the measurement plug-in.",
)
@click.option(
    "-b",
    "--base-input-dir",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    required=False,
    help="Specify the root directory containing multiple plug-in directories.",
)
@click.option(
    "-n",
    "--plugin-dir-name",
    default="",
    required=False,
    help="Name of specific plug-in directory to process, or use '.' to process all plug-ins.",
)
@click.option(
    "-u",
    "--upload-packages",
    is_flag=True,
    help="Enables uploading packages to SystemLink Feed.",
)
@click.option(
    "-a",
    "--api-url",
    default=None,
    required=False,
    help="SystemLink server API endpoint URL.",
)
@click.option(
    "-k",
    "--api-key",
    default=None,
    required=False,
    help="API key for SystemLink server.",
)
@click.option(
    "-w",
    "--workspace",
    default=None,
    required=False,
    help="Workspace name for uploading plug-in packages.",
)
@click.option(
    "-f",
    "--feed-name",
    default=None,
    required=False,
    help="Feed name for uploading plug-in packages.",
)
@click.option(
    "-o",
    "--overwrite",
    is_flag=True,
    help="Allow overwriting of existing packages in SystemLink feeds.",
)
def create_and_upload_package(
    input_path: Optional[Path],
    base_input_dir: Optional[Path],
    plugin_dir_name: Optional[str],
    upload_packages: bool,
    api_url: Optional[str],
    api_key: Optional[str],
    workspace: Optional[str],
    feed_name: Optional[str],
    overwrite: Optional[bool],
) -> None:
    """Create Python Measurement plug-in package files and upload to SystemLink Feeds."""
    try:
        logger = initialize_logger(name="console_logger")
        logger.info(StatusMessages.STARTED_EXECUTION)

        systemlink_config = SystemLinkConfig(api_key=api_key, api_url=api_url, workspace=workspace)
        upload_package_info = UploadPackageInfo(feed_name=feed_name, overwrite_packages=overwrite)

        cli_args = CliInputs(
            base_input_dir=base_input_dir,
            input_path=input_path,
            upload_packages=upload_packages,
            plugin_dir_names=plugin_dir_name,
            systemlink_config=systemlink_config,
            upload_package_info=upload_package_info,
        )

        remove_handlers(logger)
        logger = initialize_logger(name="debug_logger")
        fallback_path = cli_args.base_input_dir or cli_args.input_path
        if not fallback_path:
            raise FileNotFoundError(CommandLinePrompts.PLUGIN_DIRECTORY_REQUIRED)
        logger, log_directory_path = setup_logger_with_file_handler(
            fallback_path,
            logger=logger,
        )
        logger.debug(StatusMessages.PACKAGE_VERSION.format(version=__version__))
        logger.info(StatusMessages.LOG_FILE_PATH.format(log_dir=log_directory_path))

        systemlink_client = None
        if upload_packages:
            systemlink_client = initialize_systemlink_client(
                logger=logger,
                systemlink_config=systemlink_config,
            )

        if cli_args.base_input_dir and cli_args.plugin_dir_names:
            process_and_upload_packages(
                logger=logger,
                plugin_root_directory=cli_args.base_input_dir,
                selected_plugins=cli_args.plugin_dir_names,
                systemlink_client=systemlink_client,
                upload_package_info=upload_package_info,
            )

        if cli_args.input_path:
            package_path = build_package(
                logger=logger,
                plugin_path=cli_args.input_path,
            )
            if systemlink_client and package_path:
                upload_response = upload_to_systemlink_feed(
                    package_path=package_path,
                    systemlink_client=systemlink_client,
                    upload_package_info=upload_package_info,
                )
                logger.info(
                    StatusMessages.PACKAGE_UPLOADED.format(
                        package_name=upload_response.file_name,
                        feed_name=upload_package_info.feed_name,
                    )
                )

    except ApiException as ex:
        measurement_plugin = Path(str(cli_args.input_path)).name
        logger.debug(ex, exc_info=True)
        logger.error(
            StatusMessages.UPLOAD_FAILED.format(
                package=measurement_plugin,
                name=upload_package_info.feed_name,
            )
        )
        logger.error(ex.error.message)
        logger.error(StatusMessages.CHECK_LOG_FILE)

    except PermissionError as error:
        logger.error(StatusMessages.ACCESS_DENIED)
        logger.debug(error, exc_info=True)

    except subprocess.CalledProcessError as ex:
        logger.debug(ex, exc_info=True)
        logger.error(StatusMessages.SUBPROCESS_ERROR.format(cmd=ex.cmd, returncode=ex.returncode))
        logger.error(StatusMessages.CHECK_LOG_FILE)

    except (FileNotFoundError, KeyError, ValidationError) as ex:
        logger.debug(ex, exc_info=True)
        logger.error(str(ex))
        logger.error(StatusMessages.CHECK_LOG_FILE)

    except Exception as ex:
        logger.debug(ex, exc_info=True)
        logger.error(str(ex))
        logger.error(StatusMessages.CHECK_LOG_FILE)

    finally:
        logger.info(StatusMessages.COMPLETION)
