"""Provides functions to retrieve log directory paths with fallback options."""

from pathlib import Path
from typing import Tuple


def _get_public_documents_path() -> Path:
    public_documents_path = Path("~Public") / "Documents"
    return public_documents_path.expanduser()


def _get_user_documents_path() -> Path:
    public_documents_path = Path.home() / "Documents"
    return public_documents_path.expanduser()


def get_log_directory_path(fallback_path: Path) -> Tuple[Path, bool, bool]:
    """Determine the log directory path with fallback options and status of public/user paths.

    1. Try Getting Public documents directory. if not possible,
    2. Try Getting User documents directory. if not possible,
    3. Return the output path provided.

    Args:
        fallback_path: Fallback path for logger.

    Returns:
        Output path for logger and accessibility of public paths and user paths.
    """
    public_path_status = True
    user_path_status = True

    try:
        log_directory_path = _get_public_documents_path()
    except Exception:
        public_path_status = False
        try:
            log_directory_path = _get_user_documents_path()
        except Exception:
            user_path_status = False
            log_directory_path = fallback_path

    log_directory_path = Path(log_directory_path) / "NI-Measurement-Plugin-Packager" / "Logs"

    return log_directory_path, public_path_status, user_path_status
