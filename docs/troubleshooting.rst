Troubleshooting
===============

This document contains solutions to common issues or things you can try to fix
your problems.

.. _troubleshooting_create_a_new_virtual_environment:

Create a new Virtual Environment
--------------------------------

Nine times out of ten if you're having a problem the root cause is related to
packages that are the wrong versions, installed incorrectly somehow, or not
installed.

The first thing you should try if everything is a mess and nothing seems to be
working is install everything in a fresh virtual environment.

.. code-block:: console
    :test:

    $ python -m venv .venv
    $ . .venv/bin/activate
    $ python -m pip install -U pip setuptools wheel
    $ python -m pip install -U dffml
    $ dffml version

Logging
-------

If you are having trouble figuring out what's going on, you can enable logging.

Command line utilities can enable logging by adding the ``-log debug`` option.

Python programs can enable logging by putting the following at the top of their
file.

.. code-block:: python

   import logging
   logging.basicConfig(level=logging.DEBUG)

EntrypointNotFound
------------------

Sometimes you will try to reference a model, operation, or source you packaged
and installed. Sometimes you think you installed it but you didn't. Sometimes
you may have forgotten to update the entry points.

The quickest way to check what's going on is to list everything registered to an
entry points. This will help you verify what's installed and where it lives.

.. code-block:: console
    :test:

    $ dffml service dev entrypoints list dffml.operation
