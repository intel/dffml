# Data Flow Facilitator for Machine Learning (dffml)

[![Build Status](https://travis-ci.org/intel/dffml.svg?branch=master)](https://travis-ci.org/intel/dffml) [![CII](https://bestpractices.coreinfrastructure.org/projects/2594/badge)](https://bestpractices.coreinfrastructure.org/projects/2594)

DFFML provides APIs for dataset generation and storage, and model definition
using any machine learning framework, from high level down to low level use is
supported.

The goal of DFFML is to build a community driven library of plugins for dataset
generation and model definition. So that we as developers and researchers can
quickly and easily plug and play various pieces of data with various model
implementations.

Here's a quick demo showing how DFFML can be used to train on the iris dataset.
The more we build up the library of plugins (which anyone can maintain, they
don't have to be contributed upstream unless you want to) the more variations on
model implementations and feature data generators we all have to work with.

![Demo](https://github.com/intel/dffml/raw/master/docs/images/iris_demo.gif)

Right now we've released a wrapper around the Tensorflow DNN estimator, and a
set of feature generators which gather data from git repositories.

## Installation

DFFML currently should work with Python 3.6. However, only Python 3.7 is
officially supported. This is because there are a lot of nice helper methods
Python 3.7 implemented that we intend to use instead of re-implementing.

```python
python3.7 -m pip install -U dffml
```

You can also install the Features for Git Version Control, and Models for
Tensorflow Library all at once.

- [DFFML Features for Git Version Control](feature/git/README.md)
- [DFFML Models for Tensorflow Library](model/tensorflow/README.md)

If you want a quick how to on the iris dataset head to the
[DFFML Models for Tensorflow Library](model/tensorflow/README.md) repo.

```python
python3.7 -m pip install -U dffml[git,tensorflow]
```

If you don't have Python 3.7 we have a docker image for you, or you can install
`pyenv` which will quickly and easily give you Python 3.7. See
[docs/INSTALL.md](docs/INSTALL.md) for more details.

## Usage

See [DFFML Models for Tensorflow Library](model/tensorflow/README.md) repo
until documentation here is updated with a generic example.

## Documentation

Start with [Architechture](docs/ARCHITECHTURE.md).

## License

dffml is distributed under the [MIT License](LICENSE).

## Legal

> This software is subject to the U.S. Export Administration Regulations and
> other U.S. law, and may not be exported or re-exported to certain countries
> (Cuba, Iran, Crimea Region of Ukraine, North Korea, Sudan, and Syria) or to
> persons or entities prohibited from receiving U.S. exports (including
> Denied Parties, Specially Designated Nationals, and entities on the Bureau
> of Export Administration Entity List or involved with missile technology or
> nuclear, chemical or biological weapons).
