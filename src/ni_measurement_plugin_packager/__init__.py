"""Implementation of Measurement Plug-In Packager."""

__version__ = "1.3.0-dev3"

import subprocess  # nosec: B404
from pathlib import Path
from typing import Optional

import click
from nisystemlink_feeds_manager.clients.core import ApiException

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
from ni_measurement_plugin_packager.constants import (
    CliInterface,
    CommandLinePrompts,
    StatusMessages,
)

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


def validate_path(
    ctx: click.Context, param: click.Parameter, value: Optional[str]
) -> Optional[Path]:
    """Validate whether directory path exists."""
    if not value:
        return None
    path = Path(value)
    if not path.is_dir():
        if param.name == "base_input_dir":
            raise click.BadParameter(StatusMessages.INVALID_ROOT_DIRECTORY.format(dir=value))
        else:
            raise click.BadParameter(StatusMessages.INVALID_PLUGIN_DIRECTORY.format(dir=value))
    return path


def validate_plugin_inputs(
    ctx: click.Context,
    input_path: Optional[Path],
    base_input_dir: Optional[Path],
    plugin_dir_name: Optional[str],
) -> None:
    """Validate plugin input combinations."""
    if (
        (input_path and any([base_input_dir, plugin_dir_name]))
        or (all([base_input_dir, plugin_dir_name]) and input_path)
        or (not all([base_input_dir, plugin_dir_name]) and not input_path)
    ):
        raise click.UsageError(CommandLinePrompts.PLUGIN_DIRECTORY_REQUIRED)


def validate_systemlink_inputs(
    ctx: click.Context,
    upload_packages: bool,
    api_url: Optional[str],
    api_key: Optional[str],
    workspace: Optional[str],
    feed_name: Optional[str],
) -> None:
    """Validate SystemLink related inputs."""
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
                f"When uploading packages, all SystemLink credentials are required. Missing: {', '.join(missing)}"
            )


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "-p",
    "--input-path",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    required=False,
    callback=validate_path,
    help=CliInterface.PLUGIN_DIR,
)
@click.option(
    "-b",
    "--base-input-dir",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    required=False,
    callback=validate_path,
    help=CliInterface.PLUGINS_ROOT_DIR,
)
@click.option(
    "-n",
    "--plugin-dir-name",
    default="",
    required=False,
    help=CliInterface.SELECTED_PLUGINS,
)
@click.option("-u", "--upload-packages", is_flag=True, help=CliInterface.UPLOAD_PACKAGES)
@click.option("-a", "--api-url", required=False, help=CliInterface.API_URL)
@click.option("-k", "--api-key", required=False, help=CliInterface.API_KEY)
@click.option("-w", "--workspace", required=False, help=CliInterface.WORK_SPACE)
@click.option("-f", "--feed-name", required=False, help=CliInterface.FEED_NAME)
@click.option("-o", "--overwrite", is_flag=True, help=CliInterface.OVERWRITE_PACKAGES)
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

        validate_plugin_inputs(
            click.get_current_context(), input_path, base_input_dir, plugin_dir_name
        )
        validate_systemlink_inputs(
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
        logger.info(ex.error.message)
        logger.info(StatusMessages.CHECK_LOG_FILE)

    except PermissionError as error:
        logger.info(StatusMessages.ACCESS_DENIED)
        logger.debug(error, exc_info=True)

    except subprocess.CalledProcessError as ex:
        logger.debug(ex, exc_info=True)
        logger.info(StatusMessages.SUBPROCESS_ERROR.format(cmd=ex.cmd, returncode=ex.returncode))
        logger.info(StatusMessages.CHECK_LOG_FILE)

    except Exception as ex:
        logger.debug(ex, exc_info=True)
        logger.info(ex)
        logger.info(StatusMessages.CHECK_LOG_FILE)

    finally:
        logger.info(StatusMessages.COMPLETION)
