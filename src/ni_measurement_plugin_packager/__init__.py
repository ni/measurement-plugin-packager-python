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
    get_publish_package_client,
    publish_package_to_systemlink,
    publish_packages_from_directory,
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
from ni_measurement_plugin_packager.models import (
    CliInputs,
    SystemLinkConfig,
    UploadPackageInfo,
)

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "-p",
    "--plugin-dir",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    required=False,
    help=CliInterface.PLUGIN_DIR,
)
@click.option(
    "-b",
    "--base-dir",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    required=False,
    help=CliInterface.PLUGIN_BASE_DIR,
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
    """Create Python measurement plug-in package files and upload to SystemLink Feeds."""
    try:
        logger = initialize_logger(name="console_logger")
        logger.info(StatusMessages.STARTED_EXECUTION)

        systemlink_config = SystemLinkConfig(api_key=api_key, api_url=api_url, workspace=workspace)
        upload_package_info = UploadPackageInfo(feed_name=feed_name, overwrite_packages=overwrite)

        cli_args = CliInputs(
            measurement_plugin_base_path=base_dir,
            measurement_plugin_path=plugin_dir,
            upload_packages=upload_packages,
            selected_plugins=selected_plugins,
            systemlink_config=systemlink_config,
            upload_package_info=upload_package_info,
        )

        remove_handlers(logger)
        logger = initialize_logger(name="debug_logger")
        output_path = cli_args.measurement_plugin_base_path or cli_args.measurement_plugin_path
        if not output_path:
            raise FileNotFoundError(CommandLinePrompts.PLUGIN_DIR_REQUIRED)
        logger, log_folder_path = setup_logger_with_file_handler(
            output_path,
            logger=logger,
        )
        logger.debug(StatusMessages.VERSION.format(version=__version__))
        logger.info(StatusMessages.LOG_FILE_LOCATION.format(log_dir=log_folder_path))

        publish_package_client = None
        if upload_packages:
            publish_package_client = get_publish_package_client(
                logger=logger,
                systemlink_config=systemlink_config,
            )

        if cli_args.measurement_plugin_base_path and cli_args.selected_plugins:
            publish_packages_from_directory(
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
                    StatusMessages.PACKAGE_UPLOADED.format(
                        package_name=upload_response.file_name,
                        feed_name=upload_package_info.feed_name,
                    )
                )

    except ApiException as ex:
        measurement_plugin = Path(str(cli_args.measurement_plugin_path)).name
        logger.debug(ex, exc_info=True)
        logger.error(
            StatusMessages.PACKAGE_UPLOAD_FAILED.format(
                package=measurement_plugin,
                name=upload_package_info.feed_name,
            )
        )
        logger.info(ex.error.message)
        logger.info(StatusMessages.CHECK_LOG_FILE)

    except PermissionError as error:
        logger.info(StatusMessages.ACCESS_DENIED)
        logger.debug(error, exc_info=True)

    except subprocess.CalledProcessError as ex:
        logger.debug(ex, exc_info=True)
        logger.info(
            StatusMessages.SUBPROCESS_ERR.format(cmd=ex.cmd, returncode=ex.returncode)
        )
        logger.info(StatusMessages.CHECK_LOG_FILE)

    except (FileNotFoundError, KeyError, ValidationError) as ex:
        logger.debug(ex, exc_info=True)
        logger.info(ex)
        logger.info(StatusMessages.CHECK_LOG_FILE)

    except Exception as ex:
        logger.debug(ex, exc_info=True)
        logger.info(ex)
        logger.info(StatusMessages.CHECK_LOG_FILE)

    finally:
        logger.info(StatusMessages.PROCESS_COMPLETED)
