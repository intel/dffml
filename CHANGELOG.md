# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Async helper concurrently nocancel optional keyword argument which, if set is
  a set of tasks not to cancel when the concurrently execution loop completes.
- FileSourceTest has a `test_label` method which checks that a FileSource knows
  how to properly load and save repos under a given label.
- Test case for Merge CLI command
- Repo.feature method to select a single piece of feature data within a repo.
- Dev service to help with hacking on DFFML and to create models from templates
  in the skel/ directory.
- Classification type parameter to DNNClassifierModelConfig to specifiy data
  type of given classification options.
- util.cli CMD classes have their argparse description set to their docstring.
- util.cli CMD classes can specify the formatter class used in
  `argparse.ArgumentParser` via the `CLI_FORMATTER_CLASS` property.
- Skeleton for service creation was added
- Simple Linear Regression model from scratch
- Scikit Linear Regression model
- Community link in CONTRIBUTING.md.
- Explained three main parts of DFFML on docs homepage
- Documentation on how to use ML models on docs Models plugin page.
- Mailing list info
- Issue template for questions
- Multiple Scikit Models with dynamic config
- Entrypoint listing command to development service to aid in debugging issues
  with entrypoints.
- HTTP API service to enable interacting with DFFML over HTTP. Currently
  includes APIs for configuring and using Sources and Models.
- MySQL protocol source to work with data from a MySQL protocol compatible db
- shouldi example got a bandit operation which tells users not to install if
  there are more than 5 issues of high severity and confidence.
- dev service got the ability to run a single operation in a standalone fashion.
- About page to docs.
### Changed
- feature/codesec became it's own branch, binsec
- BaseOrchestratorContext `run_operations` strict is default to true. With
  strict as true errors will be raised and not just logged.
- MemoryInputNetworkContext got an `sadd` method which is shorthand for creating
  a MemoryInputSet with a StringInputSetContext.
- MemoryOrchestrator `basic_config` method takes list of operations and optional
  config for them.
- shouldi example uses updated `MemoryOrchestrator.basic_config` method and
  includes more explanation in comments.
- CSVSource allows for setting the Repo's `src_url` from a csv column
- util Entrypoint defines a new class for each loaded class and sets the
  `ENTRY_POINT_LABEL` parameter within the newly defined class.
- Tensorflow model removed usages of repo.classifications methods.
- Entrypoint prints traceback of loaded classes to standard error if they fail
  to load.
- Updated Tensorflow model README.md to match functionality of
  DNNClassifierModel.
- DNNClassifierModel no longer splits data for the user.
- Update `pip` in Dockerfile.
- Restructured documentation
- Ran `black` on whole codebase, including all submodules
- CI style check now checks whole codebase
- Merged HACKING.md into CONTRIBUTING.md
- shouldi example runs bandit now in addition to safety
- The way safety gets called
- Switched documentation to Read The Docs theme
- Models yield only a repo object instead of the value and confidence of the
  prediction as well. Models are not responsible for calling the predicted
  method on the repo. This will ease the process of making predict feature
  specific.
### Fixed
- Docs get version from dffml.version.VERSION.
- FileSource zipfiles are wrapped with TextIOWrapper because CSVSource expects
  the underlying file object to return str instances rather than bytes.
- FileSourceTest inherits from SourceTest and is used to test json and csv
  sources.
- A temporary directory is used to replicate `mktemp -u` functionality so as to
  provide tests using a FileSource with a valid tempfile name.
- Labels for JSON sources
- Labels for CSV sources
- util.cli CMD's correcly set the description of subparsers instead of their
  help, they also accept the `CLI_FORMATTER_CLASS` property.
- CSV source now has `entry_point` decoration
- JSON source now has `entry_point` decoration
- Strict flag in df.memory is now on by default
- Dynamically created scikit models get config args correctly
- Renamed `DNNClassifierModelContext` first init arg from `config` to `features`
- BaseSource now has `base_entry_point` decoration
### Removed
- Repo objects are no longer classification specific. Their `classify`,
  `classified`, and `classification` methods were removed.

## [0.2.1] - 2019-06-07
### Added
- Definition spec field to specify a class representative of key value pairs for
  definitions with primitives which are dictionaries
- Auto generation of documentation for operation implementations, models, and
  sources. Generated docs include information on configuration options and
  inputs and outputs for operation implementations.
- Async helpers got an `aenter_stack` method which creates and returns and
  `contextlib.AsyncExitStack` after entering all the context's passed to it.
- Example of how to use Data Flow Facilitator / Orchestrator / Operations by
  writing a Python meta static analysis tool,
  [shouldi](https://pypi.org/project/shouldi/)
### Changed
- OperationImplementation `add_label` and `add_orig_label` methods now use
  op.name instead of `ENTRY_POINT_ORIG_LABEL` and `ENTRY_POINT_NAME`.
- Make output specs and remap arguments optional for Operations CLI commands.
- Feature skeleton project is now operations skeleton project
### Fixed
- MemoryOperationImplementationNetwork instantiates OperationImplementations
  using their `withconfig()` method.
- MemorySource now decorated with `entry_point`
- MemorySource takes arguments correctly via `config_set` and `config_get`
- skel modules have `long_description_content_type` set to "text/markdown"
- Base Orchestrator `__aenter__` and `__aexit__` methods were moved to the
  Memory Orchestrator because they are specific to that config.
- Async helper `aenter_stack` uses `inspect.isfunction` so it will bind lambdas

## [0.2.0] - 2019-05-23
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
- Documentation is now generated using Sphinx
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
