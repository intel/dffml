# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Support for zip file source
- Async helper for running tasks concurrently
- Gitter badge to README
- Documentation on the Data Flow Facilitator subsystem
- codesec plugin containing operations which gather security related metrics on
  code and binaries.
- auth plugin containing an scrypt operation as an example of thread pool usage.
### Changed
- Standardized the API for most classes in DFFML via inheritance from dffml.base
- Configuration of classes is now done via the args() and config() methods
### Fixed
- Corrected maxsplit in util.cli.parser
- Check that dtype is a class in Tensorlfow DNN
- CI script no longer always exits 0 for plugin tests
- Corrected render type in setup.py to markdown

## [0.1.2] - 2019-03-29
### Added
- Contribution guidelines
- Logging documentation
- Example usage of Git features
- New Model and Feature creation script
- New Feature skeleton directory
- New Model skeleton directory
- New Feature creation tutorial
- New Model creation tutorial
- Added update functionality to the CSV source
- Added support for Gzip file source
- Added support for bz2 file source
- Travis checks for additions to CHANGELOG.md
- Travis checks for trailing whitespace
- Added support for lzma file source
- Added support for xz file source
- Added Data Flow Facilitator
### Changed
- Restructured documentation to docs folder and moved from rST to markdown
- Git feature cloc logs if no binaries are in path
### Fixed
- Enable source.file to read from /dev/fd/XX

## [0.1.1] - 2019-03-08
### Changed
- Corrected formatting in README for PyPi

## [0.1.0] - 2019-03-07
### Added
- Feature class to collect a feature in a dataset
- Git features to collect feature data from Git repos
- Model class to wrap implementations of machine learning models
- Tensorflow DNN model for generic usage of the DNN estimator
- CLI interface and framework
- Source class to manage dataset storage
