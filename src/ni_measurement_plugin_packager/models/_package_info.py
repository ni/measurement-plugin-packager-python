"""Models for package information."""

from dataclasses import dataclass


@dataclass
class PackageInfo:
    """Measurement information for building package."""

    measurement_name: str
    package_name: str
    version: str
    description: str
    author: str