DataFlow HTTP Deployment
========================

In the :doc:`/examples/shouldi` we created a command line meta static
analysis tool, ``shouldi``.

.. code-block:: console

    $ shouldi install dffml insecure-package
    dffml is okay to install
    Do not install insecure-package!
        safety_check.outputs.result: 1
        run_bandit.outputs.result: {'CONFIDENCE.HIGH': 0.0, 'CONFIDENCE.LOW': 0.0, 'CONFIDENCE.MEDIUM': 0.0, 'CONFIDENCE.UNDEFINED': 0.0, 'SEVERITY.HIGH': 0.0, 'SEVERITY.LOW': 0.0, 'SEVERITY.MEDIUM': 0.0, 'SEVERITY.UNDEFINED': 0.0, 'loc': 100, 'nosec': 0, 'CONFIDENCE.HIGH_AND_SEVERITY.LOW': 0, 'CONFIDENCE.HIGH_AND_SEVERITY.MEDIUM': 0, 'CONFIDENCE.HIGH_AND_SEVERITY.HIGH': 0}

In the :ref:`examples_shouldi_registering_opreations` section of the
operations tutorial, we registered our operations with Python's ``entrypoint``
system. This allows other Python packages and DFFML plugins to access them
without the need to hardcode in ``import`` statements.

.. code-block:: console

    $ curl -s \
      --header "Content-Type: application/json" \
      --request POST \
      --data '{"insecure-package": [{"value":"insecure-package","definition":"safety_check.inputs.package"}]}' \
      http://localhost:8080/shouldi | python3 -m json.tool
    {
        "insecure-package": {
            "safety_check.outputs.result": 1,
            "run_bandit.outputs.result": {
                "CONFIDENCE.HIGH": 0.0,
                "CONFIDENCE.LOW": 0.0,
                "CONFIDENCE.MEDIUM": 0.0,
                "CONFIDENCE.UNDEFINED": 0.0,
                "SEVERITY.HIGH": 0.0,
                "SEVERITY.LOW": 0.0,
                "SEVERITY.MEDIUM": 0.0,
                "SEVERITY.UNDEFINED": 0.0,
                "loc": 100,
                "nosec": 0,
                "CONFIDENCE.HIGH_AND_SEVERITY.LOW": 0,
                "CONFIDENCE.HIGH_AND_SEVERITY.MEDIUM": 0,
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
    :test:

    $ python -m pip install dffml-config-yaml

We'll be working from the top level directory of the ``shouldi`` package we
created in the :doc:`/examples/shouldi` example.

The source for that package is also available under the ``examples/shouldi``
directory of the DFFML source code.

If you'd like to skip :doc:`/examples/shouldi` example, clone the dffml repo
Then change directory into the ``shouldi`` source code you would have written in
the :doc:`/examples/shouldi` example.

.. We have to install dffml-feature-git with the shouldi install command or else
   it will downlaod the latest production release from PyPi

.. code-block:: console
    :test:
    :replace: cmds[0] = ["ln", "-s", ctx["root"], "dffml"]; cmds[-1].append("dffml-feature-git")

    $ git clone --depth=1 https://github.com/intel/dffml dffml
    $ cd dffml
    $ cd examples/shouldi
    $ python -m pip install -e .[dev]

Config files are named after the dataflow they are associated with. In the
:ref:`examples_shouldi_visualizing_the_dataflow` section of the
:doc:`/examples/shouldi`, we serialized the ``shouldi`` dataflow to the
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
    :test:

    $ python -m pip install dffml-service-http

HTTP Channel Config
-------------------

To deploy our ``shouldi`` dataflow via the HTTP API, we need to register a
communication channel, which is the association of a URL path to the dataflow.

We create a config file for the ``MultiComm`` we'll be using. ``MultiComm``
config files go under the ``mc`` directory of the directory being
used to deploy. Then config file itself then goes under the name of the
``MultiComm`` its associated with, ``http`` in this instance.

.. code-block:: console
    :test:

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
    :test:
    :daemon: 8080

    $ dffml service http server -port 8080 -insecure -mc-config shouldi/deploy

In another terminal, you can send a ``POST`` request containing the ``Input``
items that you want evaluated.

.. code-block:: console
    :test:
    :replace: cmds[0][-5] = cmds[0][-5].replace("8080", str(ctx["HTTP_SERVER"]["8080"]))

    $ curl -sf \
      --header "Content-Type: application/json" \
      --request POST \
      --data '{"insecure-package": [{"value":"insecure-package","definition":"safety_check.inputs.package"}]}' \
      http://localhost:8080/shouldi | python -m json.tool
    {
        "insecure-package": {
            "safety_check.outputs.result": 1,
            "run_bandit.outputs.result": {
                "CONFIDENCE.HIGH": 0.0,
                "CONFIDENCE.LOW": 0.0,
                "CONFIDENCE.MEDIUM": 0.0,
                "CONFIDENCE.UNDEFINED": 0.0,
                "SEVERITY.HIGH": 0.0,
                "SEVERITY.LOW": 0.0,
                "SEVERITY.MEDIUM": 0.0,
                "SEVERITY.UNDEFINED": 0.0,
                "loc": 100,
                "nosec": 0,
                "CONFIDENCE.HIGH_AND_SEVERITY.LOW": 0,
                "CONFIDENCE.HIGH_AND_SEVERITY.MEDIUM": 0,
                "CONFIDENCE.HIGH_AND_SEVERITY.HIGH": 0
            }
        }
    }

Combining Operations
--------------------

If you've gone through the :doc:`/examples/integration` example, you've seen the
Git and source code analysis related operations (a list of all available
operations can be found on the :doc:`/plugins/dffml_operation` plugins page).

We'll be using those operations, so we need to install them

.. code-block:: console
    :test:

    $ python -m pip install dffml-feature-git

The ``lines_of_code_to_comments`` operation will give use the ratio of the
number of lines of comments to the number of lines of code.

You need to install `tokei <https://github.com/XAMPPRocky/tokei>`_ before you
can use ``lines_of_code_to_comments``.

.. tabs::

    .. group-tab:: Linux

        .. code-block:: console
            :test:
            :replace: import os; cmds[-1].pop(0); cmds[-1][-1] = os.path.join(ctx["venv"], "bin")

            $ curl -sSL 'https://github.com/XAMPPRocky/tokei/releases/download/v10.1.1/tokei-v10.1.1-x86_64-unknown-linux-gnu.tar.gz' | tar -xvz
            tokei
            $ echo '22699e16e71f07ff805805d26ee86ecb9b1052d7879350f7eb9ed87beb0e6b84fbb512963d01b75cec8e80532e4ea29a tokei' | sha384sum -c -
            tokei: OK
            $ sudo mv tokei /usr/bin/

    .. group-tab:: MacOS

        .. code-block:: console

            $ curl -sSL 'https://github.com/XAMPPRocky/tokei/releases/download/v10.1.1/tokei-v10.1.1-x86_64-apple-darwin.tar.gz' | tar -xvz
            tokei
            $ echo '8c8a1d8d8dd4d8bef93dabf5d2f6e27023777f8553393e269765d7ece85e68837cba4374a2615d83f071dfae22ba40e2 tokei' | sha384sum -c -
            tokei: OK
            $ sudo mv tokei /usr/bin/

The ``lines_of_code_to_comments`` operation needs the output given by
``lines_of_code_by_language``, which needs a Git repos source code.

.. image:: /images/comments_to_code.svg
    :alt: Diagram showing DataFlow of comment to code ratio operations

A ``git_repository_checked_out`` is defined as:

 - record: git_repository_checked_out(type: Dict[str, str])

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
    :test:

    mkdir -p shouldi/deploy/override

Use the ``dataflow create`` command to make a new dataflow that will be combined
with the existing flow.

.. code-block:: console
    :test:

    $ dffml dataflow create \
        -configloader yaml \
        -inputs \
          directory=key \
          safety_check.outputs.result,run_bandit.outputs.result,language_to_comment_ratio=get_single_spec \
        -flow \
          '[{"dffml.mapping.create": "mapping"}]=lines_of_code_by_language.inputs.repo' \
          '[{"pypi_package_contents": "directory"}]="dffml.mapping.create".inputs.value' \
        -- \
          dffml.mapping.create \
          lines_of_code_by_language \
          lines_of_code_to_comments \
        | tee shouldi/deploy/override/shouldi.yaml

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

We've modified the flow to create the following dataflow

.. image:: /images/shouldi-dataflow-extended.svg
    :alt: Diagram showing DataFlow with use of comment to code ratio

The diagram above can be re-generated with the following commands

.. code-block:: console
    :test:

    $ dffml dataflow merge \
        shouldi/deploy/df/shouldi.json \
        shouldi/deploy/override/shouldi.yaml | \
      dffml dataflow diagram \
        -stages processing -simple -configloader json /dev/stdin

Copy and pasting the graph into the
`mermaidjs live editor <https://mermaidjs.github.io/mermaid-live-editor>`_
results in the graph.

Redeploying
-----------

We can now stop the server we had running, and start it again with the new
configs.

.. code-block:: console
    :test:
    :daemon: 8080

    $ dffml service http server -port 8080 -insecure -mc-config shouldi/deploy

Here's an example of evaluating two packages using the new DataFlow.

.. code-block:: console
    :test:
    :replace: cmds[0][-5] = cmds[0][-5].replace("8080", str(ctx["HTTP_SERVER"]["8080"]))
    :compare-output: bool(stdout.count(b"language_to_comment_ratio") == 2)

    $ curl -sf \
      --header "Content-Type: application/json" \
      --request POST \
      --data '{"insecure-package": [{"value":"insecure-package","definition":"safety_check.inputs.package"}], "dffml": [{"value":"dffml","definition":"safety_check.inputs.package"}]}' \
      http://localhost:8080/shouldi | python -m json.tool
    {
        "insecure-package": {
            "safety_check.outputs.result": 1,
            "run_bandit.outputs.result": {
                "CONFIDENCE.HIGH": 0.0,
                "CONFIDENCE.LOW": 0.0,
                "CONFIDENCE.MEDIUM": 0.0,
                "CONFIDENCE.UNDEFINED": 0.0,
                "SEVERITY.HIGH": 0.0,
                "SEVERITY.LOW": 0.0,
                "SEVERITY.MEDIUM": 0.0,
                "SEVERITY.UNDEFINED": 0.0,
                "loc": 100,
                "nosec": 0,
                "CONFIDENCE.HIGH_AND_SEVERITY.LOW": 0,
                "CONFIDENCE.HIGH_AND_SEVERITY.MEDIUM": 0,
                "CONFIDENCE.HIGH_AND_SEVERITY.HIGH": 0
            },
            "language_to_comment_ratio": 19
        },
        "dffml": {
            "safety_check.outputs.result": 0,
            "run_bandit.outputs.result": {
                "CONFIDENCE.HIGH": 24.0,
                "CONFIDENCE.LOW": 4.0,
                "CONFIDENCE.MEDIUM": 0.0,
                "CONFIDENCE.UNDEFINED": 0.0,
                "SEVERITY.HIGH": 1.0,
                "SEVERITY.LOW": 10.0,
                "SEVERITY.MEDIUM": 17.0,
                "SEVERITY.UNDEFINED": 0.0,
                "loc": 13289,
                "nosec": 0,
                "CONFIDENCE.HIGH_AND_SEVERITY.LOW": 10,
                "CONFIDENCE.HIGH_AND_SEVERITY.MEDIUM": 13,
                "CONFIDENCE.HIGH_AND_SEVERITY.HIGH": 1
            },
            "language_to_comment_ratio": 6
        }
    }
