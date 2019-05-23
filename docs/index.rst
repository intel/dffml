.. DFFML documentation master file, created by
   sphinx-quickstart on Tue May 21 16:11:19 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to DFFML's documentation!
=================================

Data Flow Facilitator for Machine Learning (DFFML) provides APIs for dataset
generation and storage, and model definition using any machine learning
framework, from high level down to low level use is supported.

The goal of DFFML is to build a community driven library of plugins for dataset
generation and model definition. So that we as developers and researchers can
quickly and easily plug and play various pieces of data with various model
implementations.

Here's a quick demo showing how DFFML can be used to train on the iris dataset.
The more we build up the library of plugins (which anyone can maintain, they
don't have to be contributed upstream unless you want to) the more variations on
model implementations and feature data generators we all have to work with.

Right now we've released a wrapper around the Tensorflow DNN estimator, and a
set of feature generators which gather data from git repositories.

## Example Usage

To start using `dffml` for data set generation with a single CLI command see
[DFFML Features for Git Version Control](feature/git/README.md).

To start using `dffml` for machine learning on existing CSV data (Iris demo)
see [DFFML Models for Tensorflow Library](model/tensorflow/README.md).

.. toctree::
   :glob:
   :maxdepth: 2
   :caption: Contents:

   usage/*
   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
