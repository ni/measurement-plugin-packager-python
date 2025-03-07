# Changelog

All notable changes to this library will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/).
And this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0-dev3] - 2024-07-19

### Changed

- Update the `Measurement Plugin` name as per the proper convention rules.

## [1.3.0-dev2] - 2024-07-19

### Fixed

- Copy the subfolders inside the measurement plug-in directory for building .nipkg file.

### Added

- Ignore copying the files/folder like `.venv, __pycache__`. 

## [1.3.0-dev1] - 2024-07-19

### Changed

- Update the discovery services Measurement Plug-in path.

## [1.3.0-dev0] - 2024-07-18

### Added

- Integrate `nisystemlink-feeds-manager` for uploading the measurement packages to SystemLink.
- Support for comma-separated inputs for `interactive mode`.

## [1.2.0-dev2] - 2024-06-18

### Changed

- Update the CLI messages for `interactive mode`

## [1.2.0-dev1] - 2024-06-18

### Added

- Support to build 'n' measurements in non-interactive mode.

## [1.2.0-dev0] - 2024-06-13

### Added

- Update of CLI with interactive and non-interactive mode using click module.
- Removal of version tracking feature by using `config.ini` file.

## [1.1.0] - 2024-05-24

### Added

- Support for selecting measurement from the provided list of measurements.
- Auto upgrade of version for measurement packages using config.ini file

## [1.0.1] - 2024-05-21

### Fixed

- Support python 3.8 version for the tool.

## [1.0.0] - 2024-05-21

### Added

- Building NI package files for python Measurement plug-ins from the provided plug-in path.
