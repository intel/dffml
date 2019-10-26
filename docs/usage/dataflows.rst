DataFlow Deployment
===================

In the :doc:`/tutorials/operations` we created a command line meta static
analysis tool, ``shouldi``.

.. code-block:: console

    $ shouldi install dffml insecure-package
    dffml is okay to install
    Do not install insecure-package!
        safety_check_number_of_issues: 1
        bandit_output: {'CONFIDENCE.HIGH': 0.0, 'CONFIDENCE.LOW': 0.0, 'CONFIDENCE.MEDIUM': 0.0, 'CONFIDENCE.UNDEFINED': 0.0, 'SEVERITY.HIGH': 0.0, 'SEVERITY.LOW': 0.0, 'SEVERITY.MEDIUM': 0.0, 'SEVERITY.UNDEFINED': 0.0, 'loc': 100, 'nosec': 0, 'CONFIDENCE.HIGH_AND_SEVERITY.HIGH': 0}

In the :ref:`tutorials_operations_registering_opreations` section of the
operations tutorial, we registered our operations with Python's ``entry_point``
system. This allows other Python packages and DFFML plugins to access them
without the need to hardcode in ``import`` statements.

.. code-block:: console

    $ curl -s \
      --header "Content-Type: application/json" \
      --request POST \
      --data '{"insecure-package": [{"value":"insecure-package","definition":"package"}]}' \
      http://localhost:8080/shouldi | python3.7 -m json.tool
    {
        "insecure-package": {
            "safety_check_number_of_issues": 1,
            "bandit_output": {
                "CONFIDENCE.HIGH": 0,
                "CONFIDENCE.LOW": 0,
                "CONFIDENCE.MEDIUM": 0,
                "CONFIDENCE.UNDEFINED": 0,
                "SEVERITY.HIGH": 0,
                "SEVERITY.LOW": 0,
                "SEVERITY.MEDIUM": 0,
                "SEVERITY.UNDEFINED": 0,
                "loc": 100,
                "nosec": 0,
                "CONFIDENCE.HIGH_AND_SEVERITY.HIGH": 0
            }
        }
    }

Config Files
------------

As we saw before, DataFlows can be serialized to config files. JSON
representations of DataFlows are not fun to hand edit. YAML looks a lot cleaner.

We're going to install the ``dffml-config-yaml`` package so that we don't have
to look at JSON.

.. code-block:: console

    $ python3.7 -m pip install dffml-config-yaml

We'll be working from the top level directory of the ``shouldi`` package we
created in the :doc:`/tutorials/operations`.

The source for that package is also available under the ``examples/shouldi``
directory of the DFFML source code.

.. code-block:: console

    $ cd examples/shouldi

Config files are named after the dataflow they are associated with. In the
:ref:`tutorials_operations_visualizing_the_dataflow` section of the
:doc:`/tutorials/operations`, we serialized the ``shouldi`` dataflow to the
``shouldi/deploy/df`` directory.

The ``df`` directory is contains the main dataflows to be deployed.

.. code-block:: console

    $ tree shouldi/deploy/
    shouldi/deploy/
    └── df
        └── shouldi.json

    1 directory, 1 file

MultiComms
----------

Another concept in DFFML is the ``MultiComm``, they are contain multiple
channels of communications. ``MultiComm``'s will typically be protocol based.
An IRC or Slack ``MultiComm`` channel of communication might be a chat room, or
when a particular word immediately follows the bots name.

Example:

::

    myuser    | mybot: shouldi install ...

The HTTP server was the first ``MultiComm`` written for DFFML. It's channels of
communication are URL paths (Example: ``/some/url/path``).

Let's install the HTTP API service.

.. code-block:: console

    $ python3.7 -m pip install dffml-service-http

HTTP Channel Config
-------------------

To deploy our ``shouldi`` dataflow via the HTTP API, we need to register a
communication channel, which is the association of a URL path to the dataflow.

We create a config file for the ``MultiComm`` we'll be using. ``MultiComm``
config files go under the ``mc`` directory of the directory being
used to deploy. Then config file itself then goes under the name of the
``MultiComm`` its associated with, ``http`` in this instance.

.. code-block:: console

    $ mkdir -p shouldi/deploy/mc/http

The file is populated with the URL path that should trigger the dataflow, how to
present the output data, and if the dataflow should return when all outputs
exist, or if it should continue waiting for more inputs (``asynchronous``, used
for websockets / http2).

**shouldi/deploy/mc/http/shouldi.yaml**

.. literalinclude:: /../examples/shouldi/shouldi/deploy/mc/http/shouldi.yaml
    :language: yaml

Serving the DataFlow
--------------------

.. warning::

    The ``-insecure`` flag is only being used here to speed up this
    tutorial. See documentation on HTTP API
    :doc:`/plugins/service/http/security` for more information.

We now start the http server and tell it that the ``MultiComm`` configuration
directory can be found in ``shouldi/deploy``.

.. code-block:: console

    $ dffml service http server -insecure -mc-config shouldi/deploy

In another terminal, you can send a ``POST`` request containing the ``Input``
items that you want evaluated.

.. code-block:: console

    $ curl -s \
      --header "Content-Type: application/json" \
      --request POST \
      --data '{"insecure-package": [{"value":"insecure-package","definition":"package"}]}' \
      http://localhost:8080/shouldi | python3.7 -m json.tool
    {
        "bandit_output": {
            "CONFIDENCE.HIGH": 0,
            "CONFIDENCE.LOW": 0,
            "CONFIDENCE.MEDIUM": 0,
            "CONFIDENCE.UNDEFINED": 0,
            "SEVERITY.HIGH": 0,
            "SEVERITY.LOW": 0,
            "SEVERITY.MEDIUM": 0,
            "SEVERITY.UNDEFINED": 0,
            "loc": 100,
            "nosec": 0,
            "CONFIDENCE.HIGH_AND_SEVERITY.HIGH": 0
        },
        "safety_check_number_of_issues": 1
    }

Combining Operations
--------------------

If you've gone through the :doc:`/usage/integration` example, you've seen the
Git and source code analysis related operations (a list of all available
operations can be found on the :doc:`/plugins/dffml_operation` plugins page).

We'll be using those operations, so we need to install them

.. code-block:: console

    $ python3.7 -m pip install dffml-feature-git

The ``lines_of_code_to_comments`` operation will give use the ratio of the
number of lines of comments to the number of lines of code.

.. note::

    You need to install `tokei <https://github.com/XAMPPRocky/tokei>`_ before
    you can use ``lines_of_code_to_comments``.

The ``lines_of_code_to_comments`` operation needs the output given by
``lines_of_code_by_language``, which needs a Git repos source code.

.. image:: /images/comments_to_code.svg
    :alt: Diagram showing DataFlow of comment to code ratio operations

A ``git_repository_checked_out`` is defined as:

 - repo: git_repository_checked_out(type: Dict[str, str])

  - URL: str
  - directory: str
  - commit: str

``lines_of_code_by_language`` just runs ``tokei`` on the ``directory``, so if we
create ``dict`` (the programming language agnostic term is ``mapping`` /
``map``) with the property of ``directory`` pointing at the source code of the ,
Python package we downloaded for ``bandit``, we'll be able to use the Git
operations within the ``shouldi`` dataflow.

Let's create the ``override`` directory which will contain the operations we
want to add to the ``shouldi`` dataflow, and how we want to connect those
operations with the existing ones.

.. code-block:: console

    $ mkdir -p shouldi/deploy/override
    $ dffml dataflow create -config yaml \
      dffml.mapping.create lines_of_code_by_language lines_of_code_to_comments \
      > shouldi/deploy/override/shouldi.yaml

The final directory structure should look like this

.. code-block:: console

    $ tree shouldi/deploy
    shouldi/deploy
    ├── df
    │   └── shouldi.json
    ├── mc
    │   └── http
    │       └── shouldi.yaml
    └── override
        └── shouldi.yaml

    5 directories, 9 files

It contains the following files.

- ``df/shouldi.json``

  - The ``shouldi`` dataflow

- ``mc/http/shouldi.yaml``

  - A config file for the ``http`` multicomm, using the dataflow named ``shouldi``

- ``override/shouldi.yaml``

  - A dataflow containing modififactions to the ``shouldi`` dataflow

The override dataflow file looks like this:

**shouldi/deploy/override/shouldi.yaml**

.. literalinclude:: /../examples/shouldi/shouldi/deploy/override/shouldi.yaml
    :language: yaml

We've modified the flow to create the following dataflow

.. image:: /images/shouldi-dataflow-extended.svg
    :alt: Diagram showing DataFlow with use of comment to code ratio

The diagram above can be re-generated with the following commands

.. code-block:: console

    $ dffml dataflow merge \
        shouldi/deploy/df/shouldi.json \
        shouldi/deploy/override/shouldi.yaml | \
      dffml dataflow diagram \
        -stages processing -simple -config yaml /dev/stdin

Copy and pasting the graph into the
`mermaidjs live editor <https://mermaidjs.github.io/mermaid-live-editor>`_
results in the graph.

Redeploying
-----------

We can now stop the server we had running, and start it again with the new
configs.

.. code-block:: console

    $ dffml service http server -insecure -mc-config shouldi/deploy

Here's an example of evaluating two packages using the new DataFlow.

.. code-block:: console

    $ curl -s \
      --header "Content-Type: application/json" \
      --request POST \
      --data '{"insecure-package": [{"value":"insecure-package","definition":"package"}], "dffml": [{"value":"dffml","definition":"package"}]}' \
      http://localhost:8080/shouldi | python3.7 -m json.tool
    {
        "dffml": {
            "bandit_output": {
                "CONFIDENCE.HIGH": 1.0,
                "CONFIDENCE.HIGH_AND_SEVERITY.HIGH": 0,
                "CONFIDENCE.LOW": 0.0,
                "CONFIDENCE.MEDIUM": 0.0,
                "CONFIDENCE.UNDEFINED": 0.0,
                "SEVERITY.HIGH": 0.0,
                "SEVERITY.LOW": 1.0,
                "SEVERITY.MEDIUM": 0.0,
                "SEVERITY.UNDEFINED": 0.0,
                "loc": 6227,
                "nosec": 0
            },
            "language_to_comment_ratio": 5,
            "safety_check_number_of_issues": 0
        },
        "insecure-package": {
            "bandit_output": {
                "CONFIDENCE.HIGH": 0.0,
                "CONFIDENCE.HIGH_AND_SEVERITY.HIGH": 0,
                "CONFIDENCE.LOW": 0.0,
                "CONFIDENCE.MEDIUM": 0.0,
                "CONFIDENCE.UNDEFINED": 0.0,
                "SEVERITY.HIGH": 0.0,
                "SEVERITY.LOW": 0.0,
                "SEVERITY.MEDIUM": 0.0,
                "SEVERITY.UNDEFINED": 0.0,
                "loc": 100,
                "nosec": 0
            },
            "language_to_comment_ratio": 19,
            "safety_check_number_of_issues": 1
        }
    }
