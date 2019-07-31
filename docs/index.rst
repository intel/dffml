.. DFFML documentation master file, created by
   sphinx-quickstart on Tue May 21 16:11:19 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to DFFML's documentation!
=================================

Data Flow Facilitator for Machine Learning (DFFML) provides APIs for dataset
generation and storage, and model definition using any machine learning
framework, from high level down to low level use is supported.

The idea of DFFML is to abstract three main parts of the machine learning
workflow. So as to reduce the amount of code that gets re-writen when applying
machine learning to a new problem.

It's an object oriented approach involving three main classes.

- ``Source`` classes handle the storage of datasets, saving and loading them
  from files, databases, remote APIs, etc.


- ``Model`` classes handle implementations of machine learning algorithms. They
  most likely implement them using a machine learning framework. DFFML is not a
  machine learning library like PyTorch or TensorFlow. It's higher level than
  those. Because of this, you most likely you won't have to write any code to
  start doing machine learning. If you want to fine tune a model or create your
  own specific implementation, all you need to do is subclass from ``Model``.


  - To get started with machine learning right away, head over to
    :ref:`plugin_models`.


- ``OperationImplementation`` classes are akin to micro services, wrapped in
  a data flow architecture. More information on these can be found in the Data
  Flow usage example. *The data flow portion of the API is less mature*.


.. toctree::
   :glob:
   :maxdepth: 2
   :caption: Contents:

   community
   usage/*
   concepts/index
   plugins/index
   api/index

The goal of DFFML is to build a community driven library of plugins for dataset
generation and model definition. So that we as developers and researchers can
quickly and easily plug and play various pieces of data with various model
implementations.

The more we build up the library of plugins (which anyone can maintain, they
don't have to be contributed upstream unless you want to) the more variations on
model implementations, feature data generators, and database backend
abstractions, we all have to work with.

Right now we've released a wrapper around the Tensorflow DNN classifier, a
simple linear regression estimator, and a set of operations which gather data
from git repositories.

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
