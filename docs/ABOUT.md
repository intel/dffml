# Is DFFML Right For Me?

If you answer yes to any of these questions DFFML can make your life easier.

- Dataset Generation

  - Need to generate a dataset
  - Need to run asynchronous operations in order to gather dataset (http
    requests, interaction with command line utilities, etc.)

- Models

  - Want to quickly prototype how machine learning could be used on a dataset
    without writing a model
  - Need to write a finely tuned model by interacting with low level APIs of
    popular machine learning frameworks.

- Storage

  - Need a way to use datasets which could be stored in different locations or
    formats.

# About

DFFML facilitates data generation, model creation, and use of models via
services. See [Architecture](ARCHITECTURE.md) to learn how it works.

- Facilitates data collection, model creation, and use of models via services.
- Provides plumbing to facilitate the collection of feature data to create
  datasets.
- Allows developers to define their ML models via a standardized API.

  - This let's users try different libraries / models to compare performance.

- Plugin based

  - Features which gather feature data (Number of Git Authors, etc.)
  - Models which expose ML models via the standard API (Tensorflow, Scikit,
    etc.)
  - Sources which load and store feature data (CSV, JSON, MySQL, etc.)

The plumbing DFFML provides enables users to swap out models and features,
in order to quickly prototype.
