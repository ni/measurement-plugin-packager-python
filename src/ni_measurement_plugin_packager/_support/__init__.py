"""Measurement Plug-In Packager helper functions."""

import sys
from pathlib import Path

import winreg


def _get_nipath(name: str) -> Path:
    if sys.platform == "win32":
        access: int = winreg.KEY_READ
        if "64" in name:
            access |= winreg.KEY_WOW64_64KEY
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\National Instruments\Common\Installer",
            access=access,
        ) as key:
            value, type = winreg.QueryValueEx(key, name)
            assert type == winreg.REG_SZ  # nosec: B101
            return Path(value)
