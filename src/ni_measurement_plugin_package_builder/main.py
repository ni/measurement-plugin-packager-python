"""Implementation of NI Measurement Plugin Package Builder."""

import os
import subprocess
import sys
from logging import Logger
from pathlib import Path
from typing import List, Optional, Tuple

import click

from ni_measurement_plugin_package_builder import __version__
from ni_measurement_plugin_package_builder.constants import (
    MEASUREMENT_NAME,
    NIPKG_EXE,
    PACKAGES,
    CliInterface,
    UserMessages,
)
from ni_measurement_plugin_package_builder.models import CliInputs
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


def __build_meas_package(logger: Logger, measurement_plugin_path) -> None:
    logger.info("")
    measurement_plugin = Path(measurement_plugin_path).name
    logger.info(UserMessages.BUILDING_MEAS.format(name=measurement_plugin))

    mlink_package_builder_path = get_ni_mlink_package_builder_path(logger=logger)
    validate_meas_plugin_files(path=measurement_plugin_path)

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


def __build_meas_packages(
    logger: Logger,
    measurement_plugin_base_path: str,
    measurement_plugins: List[str],
) -> None:
    for measurement_plugin in measurement_plugins:
        measurement_plugin_path = os.path.join(measurement_plugin_base_path, measurement_plugin)
        try:
            __build_meas_package(
                logger=logger,
                measurement_plugin_path=measurement_plugin_path,
            )
        except Exception as ex:
            logger.debug(ex, exc_info=True)
            logger.info(ex)
            logger.info(UserMessages.CHECK_LOG_FILE)


def __build_meas_in_interactive_mode(logger: Logger, measurement_plugin_base_path: str) -> None:
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
        )
        logger.info("\n")
        user_input_for_continuation = input(UserMessages.CONTINUE_BUILDING).strip().lower()
        if user_input_for_continuation != "y":
            break


def __build_meas_in_non_interactive_mode(
    logger: Logger,
    measurement_plugin_base_path: str,
    selected_meas_plugins: str,
) -> None:
    measurement_plugins = get_folders(folder_path=measurement_plugin_base_path)

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
def run(
    interactive_mode: bool,
    plugin_dir: Optional[Path],
    base_dir: Optional[Path],
    selected_meas_plugins: str,
) -> None:
    """NI Measurement Plugin Package Builder is a Command line tool for building NI package file\
 for python measurement plugins."""
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

            logger.debug(UserMessages.NON_INTERACTIVE_MODE.format(dir=plugin_dir))
            cli_args = CliInputs(
                measurement_plugin_path=plugin_dir,
                selected_meas_plugins=selected_meas_plugins,
                measurement_plugin_base_path=base_dir,
                interactive_mode=interactive_mode,
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
            )
        elif cli_args.measurement_plugin_path:
            __build_meas_package(
                logger=logger,
                measurement_plugin_path=cli_args.measurement_plugin_path,
            )
            logger.info("")

    except PermissionError as error:
        logger.info(UserMessages.ACCESS_DENIED)
        logger.debug(error, exc_info=True)

    except subprocess.CalledProcessError as ex:
        logger.debug(ex, exc_info=True)
        logger.info(UserMessages.SUBPROCESS_ERR.format(cmd=ex.cmd, returncode=ex.returncode))
        logger.info(UserMessages.CHECK_LOG_FILE)

    except FileNotFoundError as ex:
        logger.debug(ex, exc_info=True)
        logger.info(ex)

    except Exception as ex:
        logger.debug(ex, exc_info=True)
        logger.info(ex)
        logger.info(UserMessages.CHECK_LOG_FILE)

    finally:
        logger.info(UserMessages.PROCESS_COMPLETED)
