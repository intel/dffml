Command Line
============

Almost anything you can get done with the Python API you can get done with the
command line interface too.

.. contents:: Command Line Interface

Model
-----

Train, asses accuracy, and use models for prediction.

DataFlow
--------

Create, modify, run, and visualize DataFlows.

Create
~~~~~~

Ouput the dataflow description to standard output using the specified config
format.

.. code-block:: console

    $ dffml dataflow create -config yaml get_single clone_git_repo

Merge
~~~~~

Combine two dataflows into one. Dataflows must either be all linked or all not
linked.

.. code-block:: console

    $ dffml dataflow merge base.yaml overrides.yaml

Diagram
~~~~~~~

Output a mermaidjs graph description of a DataFlow.

.. code-block:: console

    $ dffml dataflow diagram -simple shouldi.json

You can now copy the graph description and paste it in the
`mermaidjs live editor <https://mermaidjs.github.io/mermaid-live-editor>`_ (or
use the CLI tool) to generate an SVG or other format of the graph.

Create
~~~~~~

Ouput the dataflow description to standard output using the specified config
format.

.. code-block:: console

    $ dffml dataflow create -config yaml get_single clone_git_repo

Config
------

.. _cli_config_convert:

Convert
~~~~~~~

Convert one config file format into another.

.. code-block:: console

    $ dffml config convert -config-out yaml config_in.json

Service
-------

Services are various command line utilities that are associated with DFFML.

For a complete list of services maintained within the core codebase see the
:doc:`/plugins/dffml_service_cli` plugin docs.

HTTP
~~~~

Everything you can do via the Python library or command line interface you can
also do over an HTTP interface. See the
:doc:`/plugins/service/http/index` docs for more information.

Dev
~~~

Development utilities for creating new packages or hacking on the core codebase.

Export
++++++

Given the
`entrypoint <https://packaging.python.org/specifications/entry-points/>`_
of an object, covert the object to it's ``dict`` representation, and export it
using the given config format.

.. code-block:: console

    $ dffml service dev export -config json shouldi.cli:DATAFLOW

.. _cli_service_dev_create:

Create
++++++

You can create a new python package and start implementing a new plugin for
DFFML right away with the ``create`` command of ``dev``.

.. code-block:: console

    $ dffml service dev create model cool-ml-model
    $ cd cool-ml-model
    $ python setup.py test

When you're done you can upload it to PyPi and it'll be ``pip`` installable so
that other DFFML users can use it in their code or via the CLI. If you don't
want to mess with uploading to ``PyPi``, you can install it from your git repo
(wherever it may be that you upload it to).

.. code-block:: console

    $ python -m pip install -U git+https://github.com/user/cool-ml-model

Make sure to look in ``setup.py`` and edit the ``entry_points`` to match
whatever you've edited. This way whatever you make will be usable by others
within the DFFML CLI and HTTP API as soon as they ``pip`` install your package,
nothing else required.

Entrypoints
+++++++++++

DFFML makes heavy use of the Python
`entrypoint <https://packaging.python.org/specifications/entry-points/>`_
system. The following tools will help you with development and use of the
entrypoints system.

List
____

Sometimes you'll find that you've installed a package in development
mode, but the code that's being run when your using the CLI or HTTP API isn't
the code you've made modifications to, but instead it seems to be the latest
released version. That's because if the latest released version is installed,
the development mode source will be ignored by Python.

If you face this problem the first thing you'll want to do is identify the
entrypoint your plugin is being loaded from. Then you'll want to run this
command giving it that entrypoint. It will list all the registered plugins for
that entrypoint, along with the location of the source code being used.

In the following example, we see that the ``is_binary_pie`` operation registered
under the ``dffml.operation`` entrypoint is using the source from the
``site-packages`` directory. When you see ``site-packages`` you'll know that the
development version is not the one being used! That's the location where release
packages get installed. You'll want to remove the directory (and ``.dist-info``
directory) of the package name you don't want to used the released version of
from the ``site-packages`` directory. Then Python will start using the
development version (provided you have installed that source with the ``-e``
flag to ``pip install``).

.. code-block:: console

    $ dffml service dev entrypoints list dffml.operation
    is_binary_pie = dffml_operations_binsec.operations:is_binary_pie.op -> dffml-operations-binsec 0.0.1 (/home/user/.pyenv/versions/3.7.2/lib/python3.7/site-packages)
    pypi_package_json = shouldi.pypi:pypi_package_json -> shouldi 0.0.1 (/home/user/Documents/python/dffml/examples/shouldi)
    clone_git_repo = dffml_feature_git.feature.operations:clone_git_repo -> dffml-feature-git 0.2.0 (/home/user/Documents/python/dffml/feature/git)
