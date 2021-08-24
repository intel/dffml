.. _model_tutorial:

Models
======

If you have some data and want to do machine learning on it, you probably want
to head over to the :ref:`plugin_models` plugins. This tutorial is for
implementing a machine learning algorithm. Which is probably what you want if
there's not an existing plugin for your algorithm.

DFFML is not like PyTorch or TensorFlow. It's higher level than those. However,
that doesn't mean it *has* to be higher level. You can use the lower level APIs
of any library, or no library if you wanted.

These tutorials will show you two use existing DFFML models, implement your own
machine learning algorithm or wrap an existing libraries implementation, and
package it so others can use it easily.

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    iris
    load
    archive
    slr
    package
    docs
