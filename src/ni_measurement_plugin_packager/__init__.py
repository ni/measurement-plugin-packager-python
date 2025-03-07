"""Implementation of Measurement Plug-In Packager."""

__version__ = "1.3.0"

import subprocess  # nosec: B404
from pathlib import Path
from typing import Optional

import click
from nisystemlink_feeds_manager.clients.core import ApiException

from ni_measurement_plugin_packager._constants import CommandLinePrompts, StatusMessages
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


CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


def _validate_path(
    ctx: click.Context, param: click.Parameter, value: Optional[str]
) -> Optional[Path]:
    if not value:
        return None
    path = Path(value)
    if not path.is_dir():
        if param.name == "base_input_dir":
            raise click.BadParameter(StatusMessages.INVALID_ROOT_DIRECTORY.format(dir=value))
        else:
            raise click.BadParameter(StatusMessages.INVALID_PLUGIN_DIRECTORY.format(dir=value))
    return path


def _validate_plugin_inputs(
    ctx: click.Context,
    input_path: Optional[Path],
    base_input_dir: Optional[Path],
    plugin_dir_name: Optional[str],
) -> None:
    if (input_path and (base_input_dir or plugin_dir_name)) or (
        not input_path and not (base_input_dir and plugin_dir_name)
    ):
        raise click.UsageError(CommandLinePrompts.PLUGIN_DIRECTORY_REQUIRED)


def _validate_systemlink_inputs(
    ctx: click.Context,
    upload_packages: bool,
    api_url: Optional[str],
    api_key: Optional[str],
    workspace: Optional[str],
    feed_name: Optional[str],
) -> None:
    if not upload_packages and any([api_key, api_url, workspace, feed_name]):
        raise click.UsageError(CommandLinePrompts.UNWANTED_SYSTEMLINK_CREDENTIALS)

    if upload_packages:
        if not all([api_key, api_url, workspace, feed_name]):
            missing = []
            if not api_key:
                missing.append("API key")
            if not api_url:
                missing.append("API URL")
            if not workspace:
                missing.append("workspace")
            if not feed_name:
                missing.append("feed name")
            raise click.UsageError(
                f"To upload packages to SystemLink, the following credentials are required: {', '.join(missing)}"
            )


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "-p",
    "--input-path",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    callback=_validate_path,
    help="Measurement plug-in directory to be packaged.",
)
@click.option(
    "-b",
    "--base-input-dir",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    callback=_validate_path,
    help="Base directory with measurement plug-ins, each in its own separate directory.",
)
@click.option(
    "-n",
    "--plugin-dir-name",
    default="",
    help="Plug-in directory name to be packaged. Used with `--base-input-dir`. Provide '.' to package all plug-ins in the base input directory.",
)
@click.option(
    "-u",
    "--upload-packages",
    is_flag=True,
    help="Enable uploading packages to the SystemLink Feed.",
)
@click.option(
    "-a",
    "--api-url",
    help="SystemLink server API endpoint URL.",
)
@click.option(
    "-k",
    "--api-key",
    help="API key for the SystemLink server.",
)
@click.option(
    "-w",
    "--workspace",
    help="Workspace name to upload the packaged plug-ins.",
)
@click.option(
    "-f",
    "--feed-name",
    help="Feed name to upload the packaged plug-in(s).",
)
@click.option(
    "-o",
    "--overwrite",
    is_flag=True,
    help="Overwrite the existing packages in the SystemLink feed.",
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

        _validate_plugin_inputs(
            click.get_current_context(), input_path, base_input_dir, plugin_dir_name
        )
        _validate_systemlink_inputs(
            click.get_current_context(), upload_packages, api_url, api_key, workspace, feed_name
        )

        remove_handlers(logger)
        logger = initialize_logger(name="debug_logger")
        fallback_path = base_input_dir or input_path
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
                api_key=api_key,
                api_url=api_url,
                workspace=workspace,
            )

        if base_input_dir and plugin_dir_name:
            process_and_upload_packages(
                logger=logger,
                plugin_root_directory=base_input_dir,
                selected_plugins=plugin_dir_name,
                systemlink_client=systemlink_client,
                feed_name=feed_name,
                overwrite_packages=overwrite,
            )

        if input_path:
            package_path = build_package(
                logger=logger,
                plugin_path=input_path,
            )
            if systemlink_client and package_path:
                upload_response = upload_to_systemlink_feed(
                    package_path=package_path,
                    systemlink_client=systemlink_client,
                    feed_name=feed_name,
                    overwrite_packages=overwrite,
                )
                logger.info(
                    StatusMessages.PACKAGE_UPLOADED.format(
                        package_name=upload_response.file_name,
                        feed_name=feed_name,
                    )
                )

    except ApiException as ex:
        measurement_plugin = Path(str(input_path)).name
        logger.debug(ex, exc_info=True)
        logger.error(
            StatusMessages.UPLOAD_FAILED.format(
                package=measurement_plugin,
                name=feed_name,
            )
        )
        logger.error(ex.error.message)
        logger.error(StatusMessages.CHECK_LOG_FILE)

    except PermissionError as error:
        logger.debug(error, exc_info=True)
        logger.error(StatusMessages.ACCESS_DENIED)

    except subprocess.CalledProcessError as ex:
        logger.debug(ex, exc_info=True)
        logger.error(StatusMessages.SUBPROCESS_ERROR.format(cmd=ex.cmd, returncode=ex.returncode))
        logger.error(StatusMessages.CHECK_LOG_FILE)

    except Exception as ex:
        logger.debug(ex, exc_info=True)
        logger.error(str(ex))
        logger.error(StatusMessages.CHECK_LOG_FILE)

    finally:
        logger.info(StatusMessages.COMPLETION)
