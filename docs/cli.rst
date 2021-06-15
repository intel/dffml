Command Line
============

Almost anything you can get done with the Python API you can get done with the
command line interface too (and HTTP API).

There are many more commands than what is listed here. Use the ``-h`` flag to
see them all.

Any command can be run with logging. Just add ``-log debug`` to it to get all
logs.

.. note::

    Some of these examples assume you have ``dffml-config-yaml`` installed.

    .. code-block:: console
        :test:

        $ python -m pip install dffml-config-yaml

Version
-------

List the version of the main package, all the plugins, and their install status.

.. code-block:: console
    :test:

    $ dffml version

Packages
--------

List the names of all the packages maintained as a part of the core dffml repo.

.. code-block:: console
    :test:

    $ dffml packages

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

Create
~~~~~~

Ouput the dataflow description to standard output using the specified
configloader format.

In the following example we create a DataFlow consisting of 2 operations,
``dffml.mapping.create``, and ``print_output``. We use ``-flow`` to edit the
DataFlow and have the input of the ``print_output`` operation come from the
ouput of the ``dffml.mapping.create`` operation. If you want to see the
difference create a diagram of the DataFlow with and without using the ``-flow``
flag during generation.

.. code-block:: console
    :test:

    $ dffml dataflow create \
        -configloader yaml \
        -flow '[{"dffml.mapping.create": "mapping"}]'=print_output.inputs.data \
        -- \
          dffml.mapping.create \
          print_output \
        | tee hello.yaml
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

.. code-block:: console
    :test:

    $ dffml dataflow run contexts \
        -no-echo \
        -dataflow hello.yaml \
        -context-def value \
        -contexts \
          world \
          $USER \
        -input \
          hello=key
    {'hello': 'world'}
    {'hello': 'user'}

We can also run the dataflow using a source

.. code-block:: console
    :test:

    $ dffml dataflow run records all \
        -no-echo \
        -record-def value \
        -inputs hello=key \
        -dataflow hello.yaml \
        -sources m=memory \
        -source-records world $USER
    {'hello': 'world'}
    {'hello': 'user'}

Merge
~~~~~

Combine two dataflows into one. Dataflows must either be all linked or all not
linked.

We'll create another dataflow that contains another ``print_output`` operation.
We'll have the name of this instance of ``print_output`` be ``second_print``. We
modify the input flow of the ``second_print`` operation to have it's data also
come from the output of the ``dffml.mapping.create`` operation.

.. code-block:: console
    :test:

    $ dffml dataflow create \
        -flow '[{"dffml.mapping.create": "mapping"}]'=second_print.inputs.data \
        -- second_print=print_output \
        | tee second_print.json

We can then merge the two dataflows into a new dataflow, ``print_twice.json``.

.. code-block:: console
    :test:

    $ dffml dataflow merge hello.yaml second_print.json | tee print_twice.json

If we run the dataflow we'll see each context printed twice now.

.. code-block:: console
    :test:
    :compare-output: bool(stdout.count(b"world") == 2)

    $ dffml dataflow run contexts \
        -no-echo \
        -dataflow print_twice.json \
        -context-def value \
        -contexts \
          world \
        -input \
          hello=key
    {'hello': 'world'}
    {'hello': 'world'}

Diagram
~~~~~~~

Output a mermaidjs graph description of a DataFlow.

.. code-block:: console
    :test:

    $ dffml dataflow diagram -simple hello.yaml

You can now copy the graph description and paste it in the
`mermaidjs live editor <https://mermaidjs.github.io/mermaid-live-editor>`_ (or
use the CLI tool) to generate an SVG or other format of the graph.

Edit
----

Edit records present in a source

.. note::

    Be sure to check the :doc:`/plugins/dffml_source` plugin page to see if the
    source your trying to edit is read only be default, and requires you to add
    another flag such as ``readwrite`` to enable editing.

Record
~~~~~~

Edit individual :py:class:`Records <dffml.record.Record>` interactively.

**images.csv**

.. code-block:: console
    :test:
    :filepath: images.csv

    key,image
    four,image1.mnistpng
    five,image2.mnistpng
    three,image3.mnistpng
    two,image4.mnistpng

The edit record command drops you into the Python debugger to edit a
:py:class:`Record <dffml.record.Record>` in any source manually when a dataflow
config file is not provided.

.. code-block:: console
    :test:
    :stdin: record.data.features["image"] += "FEEDFACE"\nc

    $ dffml edit record -sources f=csv -source-filename images.csv -source-readwrite -keys three
    > /home/user/Documents/python/dffml/dffml/cli/cli.py(45)run()
    -> await sctx.update(record)
    (Pdb) record.data.features["image"] += "FEEDFACE"
    (Pdb) c

List the records in the file to verify the edit was successful.

.. code-block:: console
    :test:
    :compare-output: bool(b"image3.mnistpngFEEDFACE" in stdout)

    $ dffml list records -sources f=csv -source-filename images.csv -source-readwrite
    [
        {
            "extra": {},
            "features": {
                "image": "image1.mnistpng"
            },
            "key": "four"
        },
        {
            "extra": {},
            "features": {
                "image": "image2.mnistpng"
            },
            "key": "five"
        },
        {
            "extra": {},
            "features": {
                "image": "image3.mnistpngFEEDFACE"
            },
            "key": "three"
        },
        {
            "extra": {},
            "features": {
                "image": "image4.mnistpng"
            },
            "key": "two"
        }
    ]

All
~~~

Update all the records in any source using the :py:class:`DataFlowSource <dffml.source.df.DataFlowSource>`.

For this example, we are using the `multiply` operation which multiplies every value in a record by a
factor which is 10 in this case. The example dataflow file looks like this:

Create a source file

**data.csv**

.. code-block::
    :test:
    :filepath: data.csv

    Expertise,Salary,Trust,Years
    1,10,0.1,0
    3,20,0.2,1
    5,30,0.3,2
    7,40,0.4,3

Create the dataflow

.. code-block:: console
    :test:

    $ dffml dataflow create \
        -configloader yaml \
        -flow '[{"seed": ["Years", "Expertise", "Trust", "Salary"]}]'=multiply.inputs.multiplicand \
        -inputs \
          10=multiplier_def \
          '{"Years": "product", "Expertise": "product", "Trust": "product", "Salary": "product"}'=associate_spec \
        -- \
          multiply \
          associate_definition \
        | tee edit_records.yaml
    definitions:
      associate_output:
        name: associate_output
        primitive: Dict[str, Any]
      associate_spec:
        name: associate_spec
        primitive: List[str]
      multiplicand_def:
        name: multiplicand_def
        primitive: generic
      multiplier_def:
        name: multiplier_def
        primitive: generic
      product:
        name: product
        primitive: generic
    flow:
      associate_definition:
        inputs:
          spec:
          - seed
      multiply:
        inputs:
          multiplicand:
          - seed:
            - Years
            - Expertise
            - Trust
            - Salary
          multiplier:
          - seed
    linked: true
    operations:
      associate_definition:
        inputs:
          spec: associate_spec
        name: associate_definition
        outputs:
          output: associate_output
        stage: output
      multiply:
        inputs:
          multiplicand: multiplicand_def
          multiplier: multiplier_def
        name: multiply
        outputs:
          product: product
        stage: processing
    seed:
    - definition: multiplier_def
      value: 10
    - definition: associate_spec
      value:
        Expertise: product
        Salary: product
        Trust: product
        Years: product

Edit records in bulk with the ``edit all`` command.

.. code-block:: console
    :test:

    $ dffml edit all \
        -sources f=csv -source-filename data.csv -source-readwrite \
        -features Years:int:1 Expertise:int:1 Trust:float:1 Salary:int:1 \
        -dataflow edit_records.yaml

List them to view the edits

.. code-block:: console
    :test:
    :compare-output: bool(all(map(lambda i: bytes(str(i) + "00,", "ascii") in stdout, range(1, 5))))

    $ dffml list records -sources f=csv -source-filename data.csv
    [
        {
            "extra": {},
            "features": {
                "Expertise": 10,
                "Salary": 100,
                "Trust": 1.0,
                "Years": 0
            },
            "key": "0"
        },
        {
            "extra": {},
            "features": {
                "Expertise": 30,
                "Salary": 200,
                "Trust": 2.0,
                "Years": 10
            },
            "key": "1"
        },
        {
            "extra": {},
            "features": {
                "Expertise": 50,
                "Salary": 300,
                "Trust": 3.0,
                "Years": 20
            },
            "key": "2"
        },
        {
            "extra": {},
            "features": {
                "Expertise": 70,
                "Salary": 400,
                "Trust": 4.0,
                "Years": 30
            },
            "key": "3"
        }
    ]

Config
------

.. _cli_config_convert:

Convert
~~~~~~~

Convert one config file format into another.

.. code-block:: console
    :test:

    $ dffml config convert -config-out json hello.yaml

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
    :test:

    $ dffml service dev create model dffml-model-mycoolmodel
    $ cd dffml-model-mycoolmodel
    $ python -m unittest discover -v

When you're done you can upload it to PyPi and it'll be ``pip`` installable so
that other DFFML users can use it in their code or via the CLI. If you don't
want to mess with uploading to ``PyPi``, you can install it from your git repo
(wherever it may be that you upload it to).

.. code-block:: console

    $ python -m pip install -U https://github.com/$USER/dffml-model-mycoolmodel/archive/main.zip

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

    $ dffml service dev export -configloader json shouldi.cli:DATAFLOW

This is an example of exporting a model. Be sure the files you're exporting from
have a ``if __name__ == "__main__":`` block, or else loading the file will
result in running the code in it instead of just exporting a global variable,
which is what you want.

.. code-block:: console

    $ dffml service dev export -configloader yaml quickstart:model

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
    :test:

    $ dffml service dev entrypoints list dffml.operation
    is_binary_pie = dffml_operations_binsec.operations:is_binary_pie.op -> dffml-operations-binsec 0.0.1 (/home/user/.pyenv/versions/3.7.2/lib/python3.7/site-packages)
    pypi_package_json = shouldi.pypi:pypi_package_json -> shouldi 0.0.1 (/home/user/Documents/python/dffml/examples/shouldi)
    clone_git_repo = dffml_feature_git.feature.operations:clone_git_repo -> dffml-feature-git 0.2.0 (/home/user/Documents/python/dffml/feature/git)

setuppy
+++++++

Utilities for working with ``setup.py`` files.

version
_______


Read a ``version.py`` file and extract the version number from the ``VERSION``
variable within it. This does not execute code, it only parses it.

.. code-block:: console
    :test:

    $ dffml service dev setuppy version dffml_model_mycoolmodel/version.py
    0.0.1

kwarg
_____

``import`` a ``setup.py`` file return the value of the specified keyword
argument.

.. code-block:: console

    $ dffml service dev setuppy kwarg name setup.py
    dffml-model-mycoolmodel

bump
++++

Utilities for bumping version numbers.

inter
_____

Update the version of DFFML used by all of the plugins. Update all the
interdepent plugin versions

.. code-block:: console

    dffml service dev bump inter

packages
________

Update the version number of a package or all packages. Increments the version
of each packages by the version string given.

.. code-block:: console

    dffml service dev bump packages -log debug -skip dffml -- 0.0.1
