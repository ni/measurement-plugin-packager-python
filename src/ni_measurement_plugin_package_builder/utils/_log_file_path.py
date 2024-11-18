"""Implementation of Get Log folder path."""

from pathlib import Path, WindowsPath
from typing import Tuple


def get_public_documents_dir() -> Path:
    """Get Public Documents directory path.

    Robust method agnostic of OS installed drive.

    Returns:
        Path: Public Documents directory path.
    """
    public_documents_path = WindowsPath("~Public") / "Documents"
    return public_documents_path.expanduser()


def get_user_docs() -> Path:
    """Get user's My Documents directory path.

    Robust method agnostic of OS installed drive.

    Returns:
        Path: user's My Documents directory path.
    """
    public_documents_path = Path.home() / "Documents"
    return public_documents_path.expanduser()


def get_log_folder_path(output_path: Path) -> Tuple[Path, bool, bool]:
    """Return log file path and status public paths and user paths.

    1. Try Getting Public documents directory. if not possible,
    2. Try Getting User documents directory. if not possible,
    3. Return the output path provided.

    Args:
        output_path (Path): Output path for logger from config file.

    Returns:
        Tuple[Path, bool, bool]: Output path for logger and status of public paths and user paths.
    """
    public_path_status = True
    user_path_status = True

    try:
        log_folder_path = get_public_documents_dir()
    except Exception:
        public_path_status = False
        try:
            log_folder_path = get_user_docs()
        except Exception:
            user_path_status = False
            log_folder_path = output_path

    log_folder_path = Path(log_folder_path) / "NI-Measurement-Plugin-Package-Builder" / "Logs"

    return log_folder_path, public_path_status, user_path_status
