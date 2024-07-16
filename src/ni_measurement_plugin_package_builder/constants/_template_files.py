"""Constants utitlized for creation of Control and Instruction files."""

MEASUREMENT_SERVICES_PATH = "C:\\ProgramData\\National Instruments\\MeasurementLink\\Services\\"
NIPKG_EXE = "C:\\Program Files\\National Instruments\\NI Package Manager\\nipkg.exe"
PACKAGES = "packages"


class FileNames:
    """Name of the files required for building measurements."""

    CONTROL = "control"
    DATA = "data"
    DEBIAN_BIN = "debian-binary"
    MEASUREMENT_FILE = "measurement.py"
    BATCH_FILE = "start.bat"


class ControlFile:
    """Control file."""

    BUILT_USING = "Built-Using"
    NIPKG = "nipkg"
    ADD_ONS = "Add-Ons"
    SECTION = "Section"
    XB_PLUGIN = "XB-Plugin"
    XB_STOREPRODUCT = "XB-StoreProduct"
    XB_USER_VISIBLE = "XB-UserVisible"
    XB_VISIBLE_RUNTIME = "XB-VisibleForRuntimeDeployment"
    ARCHITECTURE = "Architecture"
    DESCRIPTION = "Description"
    VERSION = "Version"
    XB_DISPLAY_NAME = "XB-DisplayName"
    MAINTAINER = "Maintainer"
    PACKAGE = "Package"
    YES = "yes"
    NO = "no"
    FILE = "file"


class InstructionFile:
    """Instruction file."""

    INSTRUCTION = "instructions"
    START_TAG = "<"
    END_TAG = ">"
    CLOSE_START_TAG = "</"
    CUSTOM_DIRECTORIES = "customDirectories"
    CUSTOM_DIRECTORY = "customDirectory"
    NAME = "name"
    PATH = "path"
    CLOSE_END_TAG = "/>"


class PyProjectToml:
    """Pyproject toml keys."""

    TOOL = "tool"
    POETRY = "poetry"
    NAME = "name"
    DESCRIPTION = "description"
    VERSION = "version"
    AUTHOR = "authors"
    FILE_NAME = "pyproject.toml"
    META = "metadata"
