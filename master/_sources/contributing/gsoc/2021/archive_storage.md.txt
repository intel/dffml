# Support Archive Storage for Models

The goal of this project is the modify Models and DataFlows to support saving
and loading from archives (such as `.zip` and `.tar` for example).

Currently all DFFML models have a `directory` property, which is where they
store the contents of the model's state. It does not currently hold a copy of
the model's config.

We'll want to modify the Model's context entry and exit code to have it
pack/unpack it's config and its saved state directory from/into the archive at
`location`.

## Skills

- Python

## Difficulty

Beginner/Intermediate

## Related Readings

- https://intel.github.io/dffml/master/contributing/gsoc/2021/

## Getting Started

- Read the contributing guidelines
  - https://intel.github.io/dffml/master/contributing/index.html
- Go through the quickstart
  - https://intel.github.io/dffml/master/quickstart/model.html
- Go trough the model tutorials
  - https://intel.github.io/dffml/master/tutorials/models/
- Go through the model plugins
  - https://intel.github.io/dffml/master/plugins/dffml_model.html
- Start programming to understand better what will need to happen. The following
  is a rough guide meant to give you some activities that will help you better
  understand what needs to be done so you can write a more complete proposal.
  - Rename the `directory` property to `location` for all models.
  - On `__aenter__()` of `dffml.model.model.Model`, if `location` has an
    extension, such as zip or tar, extract it to a temporary directory.
  - Write a method, `get_directory()`, which returns the location of the
    temporary directory property on the `Model` class.
  - On `__aexit__()` , pack the model state directory into the `location`, along
    with it's config.
  - Understand where all the code for models are that will potentially need to
    be changed (`dffml/model` and `model/`)
  - Make this work with test cases for the SLR model.

## Potential Mentors

- [John Andersen](https://github.com/pdxjohnny)
- [Yash Lamba](https://github.com/yashlamba)
- [Saksham Arora](https://github.com/sakshamarora1)

## Tracking and Discussion

This project is related to the following issues. Please discuss and ask
questions in the issue comments. Please also ping mentors on
[Gitter](https://gitter.im/dffml/community) when you post on the following
issues so that they are sure to see that you've commented.

- https://github.com/intel/dffml/issues/662
