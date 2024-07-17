"""Implementation of NI Measurement Plugin Package Builder."""

import subprocess
from pathlib import Path
from typing import Optional

import click
from nisystemlink_feeds_manager.clients.core import ApiException
from pydantic import ValidationError

from ni_measurement_plugin_package_builder import __version__
from ni_measurement_plugin_package_builder.constants import (
    CliInterface,
    InteractiveModeMessages,
    NonInteractiveModeMessages,
    UserMessages,
)
from ni_measurement_plugin_package_builder.models import (
    CliInputs,
    SystemLinkConfig,
    UploadPackageInfo,
)
from ni_measurement_plugin_package_builder.utils._helpers import (
    build_meas_package,
    get_publish_package_client,
    publish_package_to_systemlink,
)
from ni_measurement_plugin_package_builder.utils._interactive_mode import (
    publish_meas_packages_in_interactive_mode,
)
from ni_measurement_plugin_package_builder.utils._logger import (
    initialize_logger,
    remove_handlers,
    setup_logger_with_file_handler,
)
from ni_measurement_plugin_package_builder.utils._non_interactive_mode import (
    publish_meas_packages_in_non_interactive_mode,
)

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option("-i", "--interactive-mode", is_flag=True, help=CliInterface.INTERACTIVE_BUILDER)
@click.option("-p", "--plugin-dir", type=click.Path(), required=False, help=CliInterface.MLINK_DIR)
@click.option(
    "-b",
    "--base-dir",
    type=click.Path(),
    required=False,
    help=CliInterface.MLINK_BASE_DIR,
)
@click.option(
    "-s",
    "--selected-meas-plugins",
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
    selected_meas_plugins: Optional[str],
    upload_packages: bool,
    api_url: Optional[str],
    api_key: Optional[str],
    workspace: Optional[str],
    feed_name: Optional[str],
    overwrite: Optional[bool],
) -> None:
    """NI Measurement Plugin Package Builder is a Command line tool for building NI package file\
 for python measurement plugins and uploading it to SystemLink Feeds."""
    try:
        logger = initialize_logger(name="console_logger")
        logger.info(UserMessages.STARTED_EXECUTION)

        systemlink_config = SystemLinkConfig(api_key=api_key, api_url=api_url, workspace=workspace)
        upload_package_info = UploadPackageInfo(feed_name=feed_name, overwrite_packages=overwrite)
        cli_args = CliInputs(
            measurement_plugin_base_path=base_dir,
            interactive_mode=interactive_mode,
            measurement_plugin_path=plugin_dir,
            upload_packages=upload_packages,
            selected_meas_plugins=selected_meas_plugins,
            systemlink_config=systemlink_config,
            upload_package_info=upload_package_info,
        )

        if interactive_mode:
            meas_plugin_base_path = input(
                InteractiveModeMessages.INPUT_MEAS_PLUGIN_BASE_DIR
            ).strip()
            cli_args.measurement_plugin_base_path = meas_plugin_base_path

        remove_handlers(logger)
        logger = initialize_logger(name="debug_logger")
        logger, log_folder_path = setup_logger_with_file_handler(
            output_path=(cli_args.measurement_plugin_base_path or cli_args.measurement_plugin_path),
            logger=logger,
        )
        logger.debug(UserMessages.VERSION.format(version=__version__))
        logger.info(UserMessages.LOG_FILE_LOCATION.format(log_dir=log_folder_path))

        if cli_args.measurement_plugin_base_path and interactive_mode:
            logger.debug(InteractiveModeMessages.INTERACTIVE_MODE_ON)
            publish_meas_packages_in_interactive_mode(
                logger=logger,
                measurement_plugin_base_path=meas_plugin_base_path,
            )
        else:
            logger.debug(NonInteractiveModeMessages.NON_INTERACTIVE_MODE)
            publish_package_client = None
            if upload_packages:
                publish_package_client = get_publish_package_client(
                    logger=logger,
                    systemlink_config=systemlink_config,
                )

            if cli_args.measurement_plugin_base_path and cli_args.selected_meas_plugins:
                publish_meas_packages_in_non_interactive_mode(
                    logger=logger,
                    measurement_plugin_base_path=cli_args.measurement_plugin_base_path,
                    selected_meas_plugins=cli_args.selected_meas_plugins,
                    publish_package_client=publish_package_client,
                    upload_package_info=upload_package_info,
                )

            if cli_args.measurement_plugin_path:
                meas_package_path = build_meas_package(
                    logger=logger,
                    measurement_plugin_path=cli_args.measurement_plugin_path,
                )
                if publish_package_client:
                    upload_response = publish_package_to_systemlink(
                        meas_package_path=meas_package_path,
                        publish_package_client=publish_package_client,
                        upload_package_info=upload_package_info,
                    )
                    logger.info(
                        UserMessages.PACKAGE_UPLOADED.format(
                            package_name=upload_response.file_name,
                            feed_name=upload_package_info.feed_name,
                        )
                    )

    except ApiException as ex:
        measurement_plugin = Path(cli_args.measurement_plugin_path).name
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
