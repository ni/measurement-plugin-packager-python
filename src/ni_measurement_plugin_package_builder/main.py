"""Implementation of NI Measurement Plugin Package Builder."""

import os
import subprocess
import sys
from logging import Logger
from pathlib import Path
from typing import List, Optional, Tuple

import click
from nisystemlink_feeds_manager.clients.core import ApiException
from nisystemlink_feeds_manager.clients.feeds.models import UploadPackageResponse
from nisystemlink_feeds_manager.main import PublishPackagesToSystemLink
from nisystemlink_feeds_manager.models import PackageInfo

from ni_measurement_plugin_package_builder import __version__
from ni_measurement_plugin_package_builder.constants import (
    MEASUREMENT_NAME,
    NIPKG_EXE,
    PACKAGE_NAME,
    PACKAGES,
    CliInterface,
    UserMessages,
)
from ni_measurement_plugin_package_builder.models import (
    CliInputs,
    InvalidInputError,
    UploadPackageInputs,
)
from ni_measurement_plugin_package_builder.utils import (
    add_file_handler,
    add_stream_handler,
    create_template_folders,
    get_folders,
    get_log_folder_path,
    get_measurement_package_info,
    get_ni_mlink_package_builder_path,
    get_user_inputs_in_interactive_mode,
    initialize_logger,
    remove_handlers,
    validate_meas_plugin_files,
    validate_selected_meas_plugins,
)

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


def __add_file_handler(output_path: str, logger: Logger) -> Tuple[Logger, str]:
    log_folder_path, public_path_status, user_path_status = get_log_folder_path(output_path)
    add_file_handler(logger=logger, log_folder_path=log_folder_path)
    logger.debug(UserMessages.VERSION.format(version=__version__))

    if not public_path_status:
        logger.info(UserMessages.FAILED_PUBLIC_DIR)
    if not user_path_status:
        logger.info(UserMessages.FAILED_USER_DIR)

    return logger, log_folder_path


def __initialize_logger(name: str, folder_path: str) -> Tuple[Logger, str]:
    logger = initialize_logger(name=name)

    if folder_path:
        logger, folder_path = __add_file_handler(output_path=folder_path, logger=logger)

    add_stream_handler(logger=logger)

    return logger, folder_path


def __publish_package_to_systemlink(
    feed_name: str,
    api_key: str,
    api_url: str,
    workspace: str,
    overwrite: bool,
    meas_package_path: str,
) -> UploadPackageResponse:
    publish_packages = PublishPackagesToSystemLink(
        server_api_key=api_key,
        server_url=api_url,
        workspace_name=workspace,
    )
    upload_response = publish_packages.upload_package(
        package_info=PackageInfo(feed_name=feed_name, path=meas_package_path, overwrite=overwrite)
    )
    return upload_response


def __build_meas_package(
    logger: Logger,
    measurement_plugin_path: str,
    upload_packages: bool,
    upload_package_info: UploadPackageInputs,
) -> None:
    logger.info("")
    measurement_plugin = Path(measurement_plugin_path).name
    logger.info(UserMessages.BUILDING_MEAS.format(name=measurement_plugin))

    mlink_package_builder_path = get_ni_mlink_package_builder_path(logger=logger)
    if not validate_meas_plugin_files(path=measurement_plugin_path, logger=logger):
        logger.info(UserMessages.INVALID_MEAS_PLUGIN)
        return

    measurement_package_info = get_measurement_package_info(
        measurement_plugin_path=measurement_plugin_path,
        logger=logger,
    )
    template_folder_path = create_template_folders(
        mlink_package_builder_path=mlink_package_builder_path,
        measurement_plugin_path=measurement_plugin_path,
        measurement_package_info=measurement_package_info,
    )

    package_folder_path = os.path.join(mlink_package_builder_path, PACKAGES)
    os.makedirs(package_folder_path, exist_ok=True)

    logger.info(UserMessages.TEMPLATE_FILES_COMPLETED)
    subprocess.run(f"{NIPKG_EXE} pack {template_folder_path} {package_folder_path}", check=True)
    logger.info(
        UserMessages.PACKAGE_BUILT.format(
            name=measurement_package_info[MEASUREMENT_NAME],
            dir=package_folder_path,
        )
    )

    measurement_package_path = None
    if upload_packages:
        for name in os.listdir(package_folder_path):
            if measurement_package_info[PACKAGE_NAME] in name:
                measurement_package_path = os.path.join(package_folder_path, name)
                break

        upload_response = __publish_package_to_systemlink(
            feed_name=upload_package_info.feed_name,
            api_key=upload_package_info.api_key,
            api_url=upload_package_info.api_url,
            meas_package_path=measurement_package_path,
            overwrite=upload_package_info.overwrite_packages,
            workspace=upload_package_info.workspace,
        )
        logger.info(
            UserMessages.PACKAGE_UPLOADED.format(
                package_name=upload_response.file_name,
                feed_name=upload_package_info.feed_name,
            )
        )


def __build_meas_packages(
    logger: Logger,
    measurement_plugin_base_path: str,
    measurement_plugins: List[str],
    upload_packages: bool,
    upload_package_info: UploadPackageInputs,
) -> None:
    for measurement_plugin in measurement_plugins:
        measurement_plugin_path = os.path.join(measurement_plugin_base_path, measurement_plugin)
        try:
            __build_meas_package(
                logger=logger,
                measurement_plugin_path=measurement_plugin_path,
                upload_packages=upload_packages,
                upload_package_info=upload_package_info,
            )
        except ApiException as ex:
            logger.debug(ex, exc_info=True)
            logger.info(
                UserMessages.PACKAGE_UPLOAD_FAILED.format(
                    package=measurement_plugin,
                    name=upload_package_info.feed_name,
                )
            )
            logger.info(ex.error.message)
            logger.info(UserMessages.CHECK_LOG_FILE)

        except KeyError as ex:
            logger.info(
                UserMessages.PACKAGE_UPLOAD_FAILED.format(
                    package=measurement_plugin,
                    name=upload_package_info.feed_name,
                )
            )
            logger.debug(ex, exc_info=True)
            logger.info(UserMessages.API_URL_KEY_MISSING.format(key=ex))
            logger.info(UserMessages.CHECK_LOG_FILE)

        except FileNotFoundError as ex:
            logger.info(
                UserMessages.PACKAGE_UPLOAD_FAILED.format(
                    package=measurement_plugin,
                    name=upload_package_info.feed_name,
                )
            )
            logger.debug(ex, exc_info=True)
            logger.info(ex)

        except Exception as ex:
            logger.debug(ex, exc_info=True)
            logger.info(ex)
            logger.info(UserMessages.CHECK_LOG_FILE)


def __get_user_input_for_upload_packages() -> UploadPackageInputs:
    upload_packages_input = UploadPackageInputs()
    api_url = input(UserMessages.ENTER_API_URL).strip()
    api_key = input(UserMessages.ENTER_API_KEY).strip()
    workspace = input(UserMessages.ENTER_WORKSPACE.strip())

    if not api_key:
        raise InvalidInputError(UserMessages.NO_API_KEY)
    feed_name = input(UserMessages.ENTER_FEED_NAME).strip()

    if not feed_name:
        raise InvalidInputError(UserMessages.NO_FEED_NAME)
    overwrite_packages = input(UserMessages.OVERWRITE_MEAS).strip().lower() == "y"

    upload_packages_input.feed_name = feed_name
    upload_packages_input.overwrite_packages = overwrite_packages
    upload_packages_input.api_url = api_url
    upload_packages_input.api_key = api_key
    upload_packages_input.workspace = workspace

    return upload_packages_input


def __build_meas_in_interactive_mode(logger: Logger, measurement_plugin_base_path: str) -> None:
    upload_packages = input(UserMessages.UPLOAD_PACKAGE)
    upload_package_info = UploadPackageInputs()

    if upload_packages == "y":
        upload_packages = True
        upload_package_info = __get_user_input_for_upload_packages()
    else:
        upload_packages = False

    while True:
        measurement_plugins = get_user_inputs_in_interactive_mode(
            logger=logger,
            measurement_plugins_base_path=measurement_plugin_base_path,
        )
        if not measurement_plugins:
            break

        __build_meas_packages(
            logger=logger,
            measurement_plugin_base_path=measurement_plugin_base_path,
            measurement_plugins=measurement_plugins,
            upload_packages=upload_packages,
            upload_package_info=upload_package_info,
        )
        logger.info("\n")
        user_input_for_continuation = input(UserMessages.CONTINUE_BUILDING).strip().lower()

        if user_input_for_continuation != "y":
            break

        if upload_packages:
            user_input_for_same_feed = input(UserMessages.SAME_FEED)

            if user_input_for_same_feed != "y":
                feed_name = input(UserMessages.ENTER_FEED_NAME).strip()
                if not feed_name:
                    raise InvalidInputError(UserMessages.NO_FEED_NAME)
                overwrite_packages = input(UserMessages.OVERWRITE_MEAS).strip().lower() == "y"
                upload_package_info.feed_name = feed_name
                upload_package_info.overwrite_packages = overwrite_packages

        else:
            upload_packages = input(UserMessages.UPLOAD_PACKAGE)
            if upload_packages == "y":
                upload_packages = True
                upload_package_info = __get_user_input_for_upload_packages()
            else:
                upload_packages = False


def __build_meas_in_non_interactive_mode(
    logger: Logger,
    measurement_plugin_base_path: str,
    selected_meas_plugins: str,
    upload_packages: bool,
    upload_package_info: UploadPackageInputs,
) -> None:
    measurement_plugins = get_folders(folder_path=measurement_plugin_base_path, logger=logger)

    if not measurement_plugins:
        raise FileNotFoundError(
            UserMessages.INVALID_BASE_DIR.format(dir=measurement_plugin_base_path)
        )

    if selected_meas_plugins == ".":
        selected_meas_plugins = measurement_plugins
    else:
        validate_selected_meas_plugins(
            measurement_plugins=measurement_plugins,
            selected_meas_plugins=selected_meas_plugins,
            logger=logger,
        )
        selected_meas_plugins = [
            meas_plugin.strip("'\"").strip() for meas_plugin in selected_meas_plugins.split(",")
        ]

    __build_meas_packages(
        logger=logger,
        measurement_plugin_base_path=measurement_plugin_base_path,
        measurement_plugins=selected_meas_plugins,
        upload_packages=upload_packages,
        upload_package_info=upload_package_info,
    )
    logger.info("\n")


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
@click.option("-u", "--upload-packages", is_flag=True, help=CliInterface.UPLOADED_PACKAGES)
@click.option("-a", "--api-url", default=None, required=False, help=CliInterface.API_URL)
@click.option("-k", "--api-key", default=None, required=False, help=CliInterface.API_KEY)
@click.option("-w", "--workspace", default=None, required=False, help=CliInterface.WORK_SPACE)
@click.option("-f", "--feed-name", default=None, required=False, help=CliInterface.FEED_NAME)
@click.option("-o", "--overwrite", is_flag=True, help=CliInterface.OVERWRITE_PACKAGES)
def run(
    interactive_mode: bool,
    plugin_dir: Optional[Path],
    base_dir: Optional[Path],
    selected_meas_plugins: str,
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
        log_folder_path = None
        logger, log_folder_path = __initialize_logger(
            name="console_logger",
            folder_path=log_folder_path,
        )
        logger.info(UserMessages.STARTED_EXECUTION)

        if interactive_mode:
            if plugin_dir or base_dir or selected_meas_plugins:
                logger.warning(UserMessages.DIR_NOT_REQUIRED)
                sys.exit(1)

            logger.debug(UserMessages.INTERACTIVE_MODE_ON)
            plugin_base_path = input(UserMessages.INPUT_MEAS_PLUGIN_BASE_DIR)
            cli_args = CliInputs(
                measurement_plugin_base_path=plugin_base_path,
                interactive_mode=interactive_mode,
            )

        else:
            if not plugin_dir and not (base_dir and selected_meas_plugins):
                logger.warning(UserMessages.MEAS_DIR_REQUIRED)
                sys.exit(1)

            if not upload_packages and any([feed_name, api_key, api_url, workspace]):
                logger.warning(UserMessages.UNWANTED_SYSTEMLINK_CREDENTIALS)
                sys.exit(1)

            if upload_packages and not api_key:
                logger.warning(UserMessages.NO_API_KEY)
                sys.exit(1)

            if upload_packages and not feed_name:
                logger.warning(UserMessages.NO_FEED_NAME)
                sys.exit(1)

            logger.debug(UserMessages.NON_INTERACTIVE_MODE.format(dir=plugin_dir))
            upload_package_info = UploadPackageInputs(
                feed_name=feed_name,
                workspace=workspace,
                api_key=api_key,
                api_url=api_url,
                overwrite_packages=overwrite,
            )
            cli_args = CliInputs(
                measurement_plugin_path=plugin_dir,
                selected_meas_plugins=selected_meas_plugins,
                measurement_plugin_base_path=base_dir,
                interactive_mode=interactive_mode,
                upload_packages=upload_packages,
                upload_packages_info=upload_package_info,
            )

        remove_handlers(logger)

        logger, log_folder_path = __initialize_logger(
            name="debug_logger",
            folder_path=cli_args.measurement_plugin_path or cli_args.measurement_plugin_base_path,
        )
        logger.debug(UserMessages.VERSION.format(version=__version__))
        logger.info(UserMessages.LOG_FILE_LOCATION.format(log_dir=log_folder_path))

        if cli_args.measurement_plugin_base_path and interactive_mode:
            __build_meas_in_interactive_mode(
                logger=logger,
                measurement_plugin_base_path=cli_args.measurement_plugin_base_path,
            )
        elif cli_args.measurement_plugin_base_path and cli_args.selected_meas_plugins:
            __build_meas_in_non_interactive_mode(
                logger=logger,
                measurement_plugin_base_path=cli_args.measurement_plugin_base_path,
                selected_meas_plugins=cli_args.selected_meas_plugins,
                upload_packages=upload_packages,
                upload_package_info=upload_package_info,
            )
        elif cli_args.measurement_plugin_path:
            __build_meas_package(
                logger=logger,
                measurement_plugin_path=cli_args.measurement_plugin_path,
                upload_packages=upload_packages,
                upload_package_info=upload_package_info,
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

    except KeyError as ex:
        logger.debug(ex, exc_info=True)
        logger.info(UserMessages.API_URL_KEY_MISSING.format(key=ex))

    except FileNotFoundError as ex:
        logger.debug(ex, exc_info=True)
        logger.info(ex)

    except Exception as ex:
        logger.debug(ex, exc_info=True)
        logger.info(ex)
        logger.info(UserMessages.CHECK_LOG_FILE)

    finally:
        logger.info(UserMessages.PROCESS_COMPLETED)
