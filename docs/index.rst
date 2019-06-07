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

The more we build up the library of plugins (which anyone can maintain, they
don't have to be contributed upstream unless you want to) the more variations on
model implementations, feature data generators, and database backend
abstractions, we all have to work with.

Right now we've released a wrapper around the Tensorflow DNN estimator, and a
set of feature generators which gather data from git repositories.

.. toctree::
   :glob:
   :maxdepth: 2
   :caption: Contents:

   community
   usage/*
   concepts/index
   plugins/index
   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
