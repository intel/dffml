Command Line
============

Almost anything you can get done with the Python API you can get done with the
command line interface too (and HTTP API).

There are many more commands than what is listed here. Use the ``-h`` flag to
see them all.

Any command can be run with logging. Just add ``-log debug`` to it to get all
logs.

Model
-----

Train, asses accuracy, and use models for prediction. See the
plugin docs for :doc:`/plugins/dffml_model` for usage of individual models

The followings shows how to use the Logistic Regression model which trains on
one variable to predict another.

First, create the dataset used for training. Since this is a simple example
we're going to use the same dataset for training and test data, you should of
course have separate training and test data.

.. literalinclude:: /../examples/model/slr/dataset.sh

Train
~~~~~

We specify the name of the model we want to use (options can be found on the
:doc:`/plugins/dffml_model` plugins page). We specify the arguments the model
requires using the ``-model-xyz`` flags.

We can give multiple sources the data should come from, each source is given a
label, which is the string to the left side of the ``=``. This is so that if you
give multiple sources, you can configure each of them individually. See the
:ref:`quickstart_command_line_flags_explained` section of the quickstart for
more details on this.

.. literalinclude:: /../examples/model/slr/train.sh

Accuracy
~~~~~~~~

Assess the accuracy of a model by providing it with a test dataset.

.. literalinclude:: /../examples/model/slr/accuracy.sh

Output

.. code-block:: console

    1.0

Prediction
~~~~~~~~~~

Ask a trained model to make a prediction.

.. literalinclude:: /../examples/model/slr/predict.sh

Output

.. code-block:: console

    [
        {
            "extra": {},
            "features": {
                "ans": 0,
                "f1": 0.8
            },
            "last_updated": "2020-03-19T13:41:08Z",
            "prediction": {
                "ans": {
                    "confidence": 1.0,
                    "value": 1
                }
            },
            "key": "0"
        }
    ]

DataFlow
--------

Create, modify, run, and visualize DataFlows.

.. note::

    Some of these examples assume you have ``dffml-config-yaml`` installed.

Create
~~~~~~

Ouput the dataflow description to standard output using the specified config
format.

.. code-block:: console

    $ dffml dataflow create -config yaml get_single clone_git_repo > df.yaml

Merge
~~~~~

Combine two dataflows into one. Dataflows must either be all linked or all not
linked.

.. code-block:: console

    $ dffml dataflow merge base.yaml overrides.yaml

Run
~~~

Iterate over each record in a source and run a dataflow on it. The records
unique key can be assigned a definition using the ``-record-def`` flag.

More inputs can be given for each record using the ``-inputs`` flag.

The ``-no-echo`` flag says that we don't want the contents of the records echoed
back to the terminal when the DataFlow completes.

The ``-no-strict`` flag tell DFFML not to exit if one key fails, continue
running the dataflow until everything is complete, useful for error prone
scraping tasks.

In the following example we create a DataFlow consisting of 2 operations,
``dffml.mapping.create``, and ``print_output``. We use ``sed`` to edit the
DataFlow and have the input of the ``print_output`` operation come from the
ouput of the ``dffml.mapping.create`` operation. If you want to see the
difference create a diagram of the DataFlow with and without using the ``sed``
command during generation.

.. code-block:: console

    $ dffml dataflow create dffml.mapping.create print_output -config yaml | \
        sed 'N;s/data:\n      - seed/data:\n      - dffml.mapping.create: mapping/g' | \
        tee df.yaml
    definitions:
      DataToPrint:
        name: DataToPrint
        primitive: generic
      key:
        name: key
        primitive: str
      mapping:
        name: mapping
        primitive: map
      value:
        name: value
        primitive: generic
    flow:
      dffml.mapping.create:
        inputs:
          key:
          - seed
          value:
          - seed
      print_output:
        inputs:
          data:
          - dffml.mapping.create: mapping
    linked: true
    operations:
      dffml.mapping.create:
        inputs:
          key: key
          value: value
        name: dffml.mapping.create
        outputs:
          mapping: mapping
        stage: processing
      print_output:
        inputs:
          data: DataToPrint
        name: print_output
        outputs: {}
        stage: processing
    $ dffml dataflow run records all \
        -no-echo \
        -record-def value \
        -inputs hello=key \
        -dataflow df.yaml \
        -sources m=memory \
        -source-records world $USER
    {'hello': 'world'}
    {'hello': 'user'}

Diagram
~~~~~~~

Output a mermaidjs graph description of a DataFlow.

.. code-block:: console

    $ dffml dataflow diagram -simple shouldi.json

You can now copy the graph description and paste it in the
`mermaidjs live editor <https://mermaidjs.github.io/mermaid-live-editor>`_ (or
use the CLI tool) to generate an SVG or other format of the graph.

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
:doc:`/plugins/service/http/cli` docs for more information.

Dev
~~~

Development utilities for creating new packages or hacking on the core codebase.

.. _cli_service_dev_create:

Create
++++++

You can create a new python package and start implementing a new plugin for
DFFML right away with the ``create`` command of ``dev``.

.. code-block:: console

    $ dffml service dev create model dffml-model-mycoolmodel
    $ cd dffml-model-mycoolmodel
    $ python setup.py test

When you're done you can upload it to PyPi and it'll be ``pip`` installable so
that other DFFML users can use it in their code or via the CLI. If you don't
want to mess with uploading to ``PyPi``, you can install it from your git repo
(wherever it may be that you upload it to).

.. code-block:: console

    $ python3 -m pip install -U git+https://github.com/$USER/dffml-model-mycoolmodel

Make sure to look in ``setup.py`` and edit the ``entry_points`` to match
whatever you've edited. This way whatever you make will be usable by others
within the DFFML CLI and HTTP API as soon as they ``pip`` install your package,
nothing else required.

Export
++++++

Given the
`entrypoint <https://packaging.python.org/specifications/entry-points/>`_
of an object, covert the object to it's ``dict`` representation, and export it
using the given config format.

All DFFML objects are exportable. Here's and example of exporting a DataFlow.

.. code-block:: console

    $ dffml service dev export -config json shouldi.cli:DATAFLOW

This is an example of exporting a model. Be sure the files you're exporting from
have a ``if __name__ == "__main__":`` block, or else loading the file will
result in running the code in it instead of just exporting a global variable,
which is what you want.

.. code-block:: console

    $ dffml service dev export -config yaml quickstart:model

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

setuppy
+++++++

Utilities for working with ``setup.py`` files.

kwarg
_____

``import`` a ``setup.py`` file return the value of the specified keyword
argument.

.. code-block:: console

    $ dffml service dev setuppy kwarg name model/tensorflow/setup.py
    dffml-model-tensorflow

bump
++++

Utilities for bumping version numbers.

main
____

Update the version of DFFML used by all of the plugins.

.. code-block:: console

    dffml service dev bump main

packages
________

Update the version number of a package or all packages. Increments the version
of each packages by the version string given.

.. code-block:: console

    dffml service dev bump packages -log debug -skip dffml -- 0.0.1
