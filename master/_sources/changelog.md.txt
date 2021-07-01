# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Consolidate test case classes
- Tutorial on how to load models dynamically
  https://intel.github.io/dffml/tutorials/models/load.html
- Download progressbar in `util/net.py`
- Usecase example notebook for "Moving between models"
- Documentation and testing support for notebooks
- Example on how to create operations and use data preprocessing source to train models
  https://intel.github.io/dffml/examples/ice_cream.html
- Operations for zip and tar file creation and extraction
- Operations for file (de)compression
### Changed
- Calls to hashlib now go through helper functions
- Build docs using `dffml service dev docs`
- `cached_download/unpack_archive()` are now functions
### Fixed
- Record object key properties are now always strings

## [0.4.0] - 2021-02-18
### Added
- New model for Anomaly Detection
- Ablity to specify maximum number of contexts running at a time
- CLI and Python example usage of Custom Neural Network
- PyTorch loss function entrypoint style loading
- Custom Neural Network, last layer support for pre-trained models
- Example usage of sklearn operations
- Example Flower17 species image classification
- Configloading ablity from CLI using "@" before filename
- Docstrings and doctestable example for DataFlowSource
- XGBoost Regression Model
- Pre-Trained PyTorch torchvision Models
- Spacy model for NER
- Ability to rename outputs using GetSingle
- Tutorial for using NLP operations with models
- Operations plugin for NLP wrapping spacy and scikit functions
- Support for default value in a Definition
- Source for reading images in directories
- Operations plugin for image preprocessing
- `-pretty` flag to `list records` and `predict` commands
- daal4py based linear regression model
- DataFlowSource can take a config file as dataflow via the CLI.
- Support for link on conditions in dataflow diagrams
- `edit all` command to edit records in bulk
- Support for Tensorflow 2.2
- Vowpal Wabbit Models
- Python 3.8 support
- binsec branch to `operations/binsec`
- Doctestable example for `model_predict` operation.
- Doctestable examples to `operation/mapping.py`
- shouldi got an operation to run Dependency-check on java code.
- `load` and `run` functions in high level API
- Doctestable examples to `db` operations.
- Source for parsing `.ini` file formats
- Tests for noasync high level API.
- Tests for load and save functions in high level API.
- `Operation` inputs and ouputs default to empty `dict` if not given.
- Ability to export any object with `dffml service dev export`
- Complete example for dataflow run cli command
- Tests for default configs instantiation.
- Example ffmpeg operation.
- Operations to deploy docker container on receving github webhook.
- New use case `Redeploying dataflow on webhook` in docs.
- Documentation for creating Source for new File types taking `.ini` as an example.
- New input modes, output modes for HTTP API dataflow registration.
- Usage example for tfhub text classifier.
- `AssociateDefinition` output operation to map definition names to values
  produced as a result of passing Inputs with those definitions to operations.
- DataFlows now have a syntax for providing a set of definitions that will
  override the operations default definition for a given input.
- Source which modifies record features as they are read from another source.
  Useful for modifying datasets as they are used with ML commands or editing
  in bulk.
- Auto create Definition for the `op` when they might have a spec, subspec.
- `shouldi use` command which detects the language of the codebase given via
  path to directory or Git repo URL and runs the appropriate static analyzers.
- Support for entrypoint style loading of operations and seed inputs in `dataflow create`.
- Definition for output of the function that `op` wraps.
- Expose high level load, run and save functions to noasync.
- Operation to verify secret for GitHub webhook.
- Option to modify flow and add config in `dataflow create`.
- Ability to use a function as a data source via the `op` source
- Make every model's directory property required
- New model AutoClassifierModel based on `AutoSklearn`.
- New model AutoSklearnRegressorModel based on `AutoSklearn`.
- Example showing usage of locks in dataflow.
- `-skip` flag to `service dev install` command to let users not install certain
  core plugins
- HTTP service got a `-redirect` flag which allows for URL redirection via a
  HTTP 307 response
- Support for immediate response in HTTP service
- Daal4py example usage.
- Gitter chatbot tutorial.
- Option to run dataflow without sources from cli.
- Sphinx extension for automated testing of tutorials (consoletest)
- Example of software portal using DataFlows and HTTP service
- Retry parameter to `Operation`. Allows for setting number of times operation
  should be retried before it's exception should be raised.
### Changed
- Renamed `-seed` to `-inputs` in `dataflow create` command
- Renamed configloader/png to configloader/image and added support for loading JPEG and TIFF file formats
- Update record `__str__` method to output in tabular format
- Update MNIST use case to normalize image arrays.
- `arg_` notation replaced with `CONFIG = ExampleConfig` style syntax
  for parsing all command line arguments.
- Moved usage/io.rst to docs/tutorials/dataflows/io.rst
- `edit` command substituted with `edit record`
- `Edit on Github` button now hidden for plugins.
- Doctests now run via unittests
- Every class and function can now be imported from the top level module
- `op` attempts to create `Definition`s for each argument if an `inputs` are not
  given.
- Classes now use `CONFIG` if it has a default for every field and `config` is `None`
- Models now dynamically import third party modules.
- Memory dataflow classes now use auto args and config infrastructure
- `dffml list records` command prints Records as JSON using `.export()`
- Feature class in `dffml/feature/feature.py` initialize a feature object
- All DefFeatures() functions are substituted with Features()
- All feature.type() and feature.lenght() are substituted with
  feature.type and feature.length
- FileSource takes pathlib.Path as filename
- Tensorflow tests re-run themselves up to 6 times to stop them from failing the
  CI due to their randomly initialized weights making them fail ~2% of the time
- Any plugin can now be loaded via it's entrypoint style path
- `with_features` now raises a helpful error message if no records with matching
  features were found
- Split out model tutorial into writing the model, and another tutorial for
  packaging the model.
- IntegrationCLITestCase creates a new directory and chdir into it for each test
- Automated testing of Automating Classification tutorial
- `dffml version` command now prints git repo hash and if the repo is dirty
### Fixed
- `export_value` now converts numpy array to JSON serializable datatype
- CSV source overwriting configloaded data to every row
- Race condition in `MemoryRedundancyChecker` when more than 4 possible
  parameter sets for an operation.
- Typing of config vlaues for numpy parsed docstrings where type should be tuple
  or list
- Model predict methods now use `SourcesContext.with_features`
### Removed
- Monitor class and associated tests (unused)
- DefinedFeature class in `dffml/feature/feature.py`
- DefFeature function in `dffml/feature/feature.py`
- load_def function in Feature class in `dffml/feature/feature.py`

## [0.3.7] - 2020-04-14
### Added
- IO operations demo and `literal_eval` operation.
- Python prompts `>>>` can now be enabled or disabled for easy copying of code into interactive sessions.
- Whitespace check now checks .rst and .md files too.
- `GetMulti` operation which gets all Inputs of a given definition
- Python usage example for LogisticRegression and its related tests.
- Support for async generator operations
- Example CLI commands and Python code for `SLRModel`
- `save` function in high level API to quickly save all given records to a
  source
- Ability to configure sources and models for HTTP API from command line when
  starting server
- Documentation page for command line usage of HTTP API
- Usage of HTTP API to the quickstart to use trained model
### Changed
- Renamed `"arg"` to `"plugin"`.
- CSV source sorts feature names within headers when saving
- Moved HTTP service testing code to HTTP service `util.testing`
### Fixed
- Exporting plugins
- Issue parsing string values when using the `dataflow run` command and
  specifying extra inputs.
### Removed
- Unused imports

## [0.3.6] - 2020-04-04
### Added
- Operations for taking input from the user `AcceptUserInput` and for printing the output `print_output`
- PNG ConfigLoader for reading images as arrays to predict using MNIST trained models
- Docstrings and doctestable examples to `record.py`.
- Inputs can be validated using operations
  - `validate` parameter in `Input` takes `Operation.instance_name`
- New db source can utilize any database that inherits from `BaseDatabase`
- Logistic Regression with SAG optimizer
- Test tensorflow DNNEstimator documentation examples in CI
- shouldi got an operation to run cargo-audit on rust code.
- Moved all the downloads to tests/downloads to speed the CI test.
- Test tensorflow DNNEstimator documentation exaples in CI
- Add python code for tensorflow DNNEstimator
- Ability to run a subflow as if it were an operation using the
  `dffml.dataflow.run` operation.
- Support for operations without inputs.
- Partial doctestable examples to `features.py`
- Doctestable examples for `BaseSource`
- Instructions for setting up debugging environment in VSCode
### Fixed
- New model tutorial mentions file paths that should be edited.
- DataFlow is no longer a dataclass to prevent it from being exported
  incorrectly.
- `operations_parameter_set_pairs` moved to `MemoryOrchestratorContext`
- Ignore generated files in `docs/plugins/`
- Treat `"~"` as the the home directory rather than a literal
- Windows support by selecting `asyncio.ProactorEventLoop` and not using
  `asyncio.FastChildWatcher`.
- Moved SLR into the main dffml package and removed `scratch:slr`.
### Changed
- Refactor `model/tensroflow`

## [0.3.5] - 2020-03-10
### Added
- Parent flows can now forward inputs to active contexts of subflows.
  - `forward` parameter in `DataFlow`
  - `subflow` in `OperationImplementationContext`
- Documentation on writing examples and running doctests
- Doctestable Examples to high-level API.
- Shouldi got an operation to run npm-audit on JavaScript code
- Docstrings and doctestable examples for `record.py` (features and evaluated)
- Simplified model API with SimpleModel
- Documentation on how DataFlows work conceptually.
- Style guide now contains information on class, variable, and function naming.
### Changed
- Restructured contributing documentation
- Use randomly generated data for scikit tests
- Change Core to Official to clarify who maintains each plugin
- Name of output of unsupervised model from "Prediction" to "cluster"
- Test scikit LR documentation examples in CI
- Create a fresh archive of the git repo for release instead of cleaning
  existing repo with `git clean` for development service release command.
- Simplified SLR tests for scratch model
- Test tensorflow DNNClassifier documentation exaples in CI
- config directories and files associated with ConfigLoaders have been renamed
  to configloader.
- Model config directory parameters are now `pathlib.Path` objects
- New model tutorial and `skel/model` use simplifeid model API.

## [0.3.4] - 2020-02-28
### Added
- Tensorflow hub NLP models.
- Notes on development dependencies in `setup.py` files to codebase notes.
- Test for `cached_download`
- `dffml.util.net.cached_download_unpack_archive` to run a cached download and
  unpack the archive, very useful for testing. Documented on the Networking
  Helpers API docs page.
- Directions on how to read the CI under the Git and GitHub page of the
  contributing documentation.
- HTTP API
  - Static file serving from a dirctory with `-static`
  - `api.js` file serving with the `-js` flag
  - Docs page for JavaScript example
- shouldi got an operation to run golangci-lint on Golang code
- Note about using black via VSCode
### Fixed
- Port assignment for the HTTP API via the `-port` flag
### Changed
- `repo`/`Repo` to `record`/`Record`
- Definitions with a `spec` can use the `subspec` parameter to declare that they
  are a list or a dict where the values are of the `spec` type. Rather than the
  list or dict itself being of the `spec` type.
- Fixed the URL mentioned in example to configure a model.
- Sphinx doctests are now run in the CI in the DOCS task.
- Lint JavaScript files with js-beautify and enforce with CI
### Removed
- Unused imports

## [0.3.3] - 2020-02-10
### Added
- Moved from TensorFlow 1 to TensorFlow 2.
- IDX Sources to read binary data files and train models on MNIST Dataset
- scikit models
  - Clusterers
    - KMeans
    - Birch
    - MiniBatchKMeans
    - AffinityPropagation
    - MeanShift
    - SpectralClustering
    - AgglomerativeClustering
    - OPTICS
- `allowempty` added to source config parameters.
- Quickstart document to show how to use models from Python.
- The latest release of the documentation now includes a link to the
  documentation for the master branch (on GitHub pages).
- Virtual environment, GitPod, and Docker development environment setup notes to
  the CONTRIBUTING.md file.
- Changelog now included in documenation website.
- Database abstraction `dffml.db`
  - SQLite connector
  - MySQL connector
- Documented style for imports.
- Documented use of numpy docstrings.
- `Inputs` can now be sanitized using function passed in `validate` parameter
- Helper utilities to take callables with numpy style docstrings and
  create config classes out of them using `make_config`.
- File listing endpoint to HTTP service.
- When an operation throws an exception the name of the instance and the
  parameters it was executed with will be thrown via an `OperationException`.
- Network utilities to preformed cached downloads with hash validation.
- Development service got a new command, which can retrieve an argument passed
  to setuptools `setup` function within a `setup.py` file.
### Changed
- All instances of `src_url` changed to `key`.
- `readonly` parameter in source config is now changed to `readwrite`.
- `predict` parameter of all model config classes has been changed from `str` to `Feature`.
- Defining features on the command line no longer requires that defined features
  be prefixed with `def:`
- The model predict operation will now raise an exception if the model it is
  passed via it's config is a class rather than an instance.
- `entry_point` and friends have been renamed to `entrypoint`.
- Use `FastChildWatcher` when run via the CLI to prevent `BlockingIOError`s.
- TensorFlow based neural network classifier had the `classification` parameter
  in it's config changed to `predict`.
- SciKit models use `make_config_numpy`.
- Predictions in `repos` are now dictionary.
- All instances of `label` changed to `tag`
- Subclasses of `BaseConfigurable` will now auto instantiate their respective
  config classes using `kwargs` if the config argument isn't given and keyword
  arguments are.
- The quickstart documentation was improved as well as the structure of docs.
### Fixed
- CONTRIBUTING.md has `-e` in the wrong place in the getting setup section.
- Since moving to auto `args()` and `config()`, BaseConfigurable no longer
  produces odd typenames in conjunction with docs.py.
- Autoconvert Definitions with spec into their spec
### Removed
- The model predict operation erroneously had a `msg` parameter in it's config.
- Unused imports identified by deepsource.io
- Evaluation code from feature.py file as well as tests for those evaluations.

## [0.3.2] - 2020-01-03
### Added
- scikit models
  - Classifiers
    - LogisticRegression
    - GradientBoostingClassifier
    - BernoulliNB
    - ExtraTreesClassifier
    - BaggingClassifier
    - LinearDiscriminantAnalysis
    - MultinomialNB
  - Regressors
    - ElasticNet
    - BayesianRidge
    - Lasso
    - ARDRegression
    - RANSACRegressor
    - DecisionTreeRegressor
    - GaussianProcessRegressor
    - OrthogonalMatchingPursuit
    - Lars
    - Ridge
- `AsyncExitStackTestCase` which instantiates and enters async and non-async
  `contextlib` exit stacks. Provides temporary file creation.
- Automatic releases to PyPi via GitHub Actions
- Automatic documentation deployment to GitHub Pages
- Function to create a config class dynamically, analogous to `make_dataclass`
- `ConfigLoaders` class which loads config files from a file or directory to a dictionary.
### Changed
- CLI tests and integration tests derive from `AsyncExitStackTestCase`
- SciKit models now use the auto args and config methods.
### Fixed
- Correctly identify when functions decorated with `op` use `self` to reference
  the `OperationImplementationContext`.
- shouldi safety operation uses subprocess communicate method instead of stdin pipe writes.
- Negative values are correctly parsed when input via the command line.
- Do not lowercase development mode install location when reporting version.

## [0.3.1] - 2019-12-12
### Added
- Integration tests using the command line interface.
- `Operation` `run_dataflow` to run a dataflow and test for the same.
### Changed
- Features were moved from ModelContext to ModelConfig
- CI is now run via GitHub Actions
- CI testing script is now verbose
- args and config methods of all classes no longer require implementation.
  BaseConfigurable handles exporting of arguments and creation of config objects
  for each class based off of the CONFIG property of that class. The CONFIG
  property is a class which has been decorated with dffml.base.config to make it
  a dataclass.
- Speed up development service install of all plugins in development mode
- Speed up named plugin load times
### Fixed
- DataFlows with multiple possibilities for a source for an input, now correctly
  look through all possible sources instead of just the first one.
- DataFlow MemoryRedundancyCheckerContext was using all inputs in an input set
  and all their ancestors to check redundancy (a hold over from pre uid days).
  It now correctly only uses the inputs in the parameter set. This fixes a major
  performance issue.
- MySQL packaging issue.
- Develop service running one off operations correctly json-loads dict types.
- Operations with configs can be run via the development service
- JSON dumping numpy int\* and float\* caused crash on dump.
- CSV source always loads `src_urls` as strings.
### Removed
- CLI command `operations` removed in favor of `dataflow run`
- Duplicate dataflow diagram code from development service

## [0.3.0] - 2019-10-26
### Added
- Real DataFlows, see operations tutorial and usage examples
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
- Tensorflow DNNEstimator based regression model.
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
- Updated Tensorflow model README.md to include usage of regression model
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
- CSV source now has `entrypoint` decoration
- JSON source now has `entrypoint` decoration
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
- MemorySource now decorated with `entrypoint`
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
- Update functionality to the CSV source
- Support for Gzip file source
- Support for bz2 file source
- Travis checks for additions to CHANGELOG.md
- Travis checks for trailing whitespace
- Support for lzma file source
- Support for xz file source
- Data Flow Facilitator
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
