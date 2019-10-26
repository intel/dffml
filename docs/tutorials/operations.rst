New Operations Tutorial
=======================

This tutorial will explain what operations are and how you can use them. In the
process we'll create a meta static analysis tool, ``shouldi``.

Operations are the core of DFFML, they have inputs and outputs, are configurable
and are run by the Orchestrator in what amounts to a large event loop.
The events in the event loop are pieces of data entering the network. When a
piece of data which matches the data types of one of the operation's inputs
enters the network, that operation is then run.

We're going to write a few operations which will run some Python static analysis
tools. With the goal being to create a command line utility called ``shouldi``
which will provide us with the information we need to make the decision, should
I install Python package X? When it's done it'll look like this

.. code-block:: console

    $ shouldi install dffml insecure-package
    dffml is okay to install
    Do not install insecure-package!
        safety_check_number_of_issues: 1
        bandit_output: {'CONFIDENCE.HIGH': 0.0, 'CONFIDENCE.LOW': 0.0, 'CONFIDENCE.MEDIUM': 0.0, 'CONFIDENCE.UNDEFINED': 0.0, 'SEVERITY.HIGH': 0.0, 'SEVERITY.LOW': 0.0, 'SEVERITY.MEDIUM': 0.0, 'SEVERITY.UNDEFINED': 0.0, 'loc': 100, 'nosec': 0, 'CONFIDENCE.HIGH_AND_SEVERITY.HIGH': 0}

In the second half of this tutorial, we'll deploy the tool as an HTTP API
endpoint rather than a command line application.

.. code-block:: console

    $ curl -s \
      --header "Content-Type: application/json" \
      --request POST \
      --data '{"insecure-package": [{"value":"insecure-package","definition":"package"}]}' \
      http://localhost:8080/shouldi | python -m json.tool
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

Tools
-----

We'll write this meta static analysis tool by collecting and interpreting the
output of static analysis tools. The two tools we'll use are ``safety`` and
``bandit``.

``safety`` is a tool that checks for known vulnerabilities in packages published
on PyPi. This is how running safety on the command line works, we supply the
package name and version.

.. code-block:: console

    $ echo insecure-package==0.1.0 | safety check --stdin
    ╒══════════════════════════════════════════════════════════════════════════════╕
    │                                                                              │
    │                               /$$$$$$            /$$                         │
    │                              /$$__  $$          | $$                         │
    │           /$$$$$$$  /$$$$$$ | $$  \__//$$$$$$  /$$$$$$   /$$   /$$           │
    │          /$$_____/ |____  $$| $$$$   /$$__  $$|_  $$_/  | $$  | $$           │
    │         |  $$$$$$   /$$$$$$$| $$_/  | $$$$$$$$  | $$    | $$  | $$           │
    │          \____  $$ /$$__  $$| $$    | $$_____/  | $$ /$$| $$  | $$           │
    │          /$$$$$$$/|  $$$$$$$| $$    |  $$$$$$$  |  $$$$/|  $$$$$$$           │
    │         |_______/  \_______/|__/     \_______/   \___/   \____  $$           │
    │                                                          /$$  | $$           │
    │                                                         |  $$$$$$/           │
    │  by pyup.io                                              \______/            │
    │                                                                              │
    ╞══════════════════════════════════════════════════════════════════════════════╡
    │ REPORT                                                                       │
    │ checked 1 packages, using default DB                                         │
    ╞════════════════════════════╤═══════════╤══════════════════════════╤══════════╡
    │ package                    │ installed │ affected                 │ ID       │
    ╞════════════════════════════╧═══════════╧══════════════════════════╧══════════╡
    │ insecure-package           │ 0.1.0     │ <0.2.0                   │ 25853    │
    ╘══════════════════════════════════════════════════════════════════════════════╛

``bandit`` is a tool that does static analysis on the source code of Python
projects to check for things like SQL injections. This is how running ``bandit``
on the command line works, we supply the path to the source directory to scan.

.. code-block:: console

    $ bandit -r distributed-android-testing/
    [main]  INFO    profile include tests: None
    [main]  INFO    profile exclude tests: None
    [main]  INFO    cli include tests: None
    [main]  INFO    cli exclude tests: None
    [main]  INFO    running on Python 3.7.3
    67 [0.. 50.. ]
    Run started:2019-10-04 19:41:06.701058

    Test results:
    >> Issue: [B108:hardcoded_tmp_directory] Probable insecure usage of temp file/directory.
       Severity: Medium   Confidence: Medium
       Location: distributed-android-testing/docker/docker.py:20
       More Info: https://bandit.readthedocs.io/en/latest/plugins/b108_hardcoded_tmp_directory.html
    19              "chmod 700 /tmp/docker_install.sh",
    20              "/tmp/docker_install.sh",
    21              "usermod -aG docker ${USER}",
    22              "service docker restart"
    23          ]
    24          kwargs["sudo"] = True
    25          ssh.run_all(command, **kwargs)

    --------------------------------------------------
    >> Issue: [B104:hardcoded_bind_all_interfaces] Possible binding to all interfaces.
       Severity: Medium   Confidence: Medium
       Location: distributed-android-testing/docker/gitlab_webhooks/app.py:23
       More Info: https://bandit.readthedocs.io/en/latest/plugins/b104_hardcoded_bind_all_interfaces.html
    22      PORT = 9898
    23      ADDRESS = "0.0.0.0"
    24      STREAM = True

Plan
----

Our plan is to run these tools and make a decision as to if we should install
the package or not based on their reports.

The first step will be to write an ``Operation`` which wraps each tool.

An ``Operation`` is similar to a function signature, it consists of a name,
inputs, and outputs. The ``op`` decorator is a shorthand way of creating an
``Operation`` from a function. An ``Operation`` is analogous to a function
prototype in C.

Creating our Package
--------------------

Create a new package using the create script.

.. code-block:: console

    $ dffml service dev create operations shouldi
    $ cd shouldi

.. note::

    All the code for this example is located under the
    `examples/shouldi <https://github.com/intel/dffml/blob/master/examples/shouldi/>`_
    directory of the DFFML source code.

Remove the example files as we won't be needing them

.. code-block:: console

    $ rm shouldi/operations.py shouldi/definitions.py tests/test_operations.py

Installing Static Analysis Tools
--------------------------------

The tools we'll be using are ``bandit`` and ``safety``. We'll also need to make
http requests so let's install ``aiohttp`` too.

Some people are familiar with the ``requirements.txt`` file used to declare
dependences. For packages, we can declare our dependencies right in our
``setup.py`` file.

**setup.py**

.. literalinclude:: /../examples/shouldi/setup.py
    :lines: 12-16

.. note::

    These versions will change over time, you should always check PyPi to find
    the latest version and use that version.

.. TODO Add link to pip oddities doc here once it exists

Now install the newly created package in development mode.

.. code-block:: console

    $ python3.7 -m pip install -e .

Safety Operation
----------------

To get parsable output, we'll run ``safety`` with the ``--json`` flag.

.. code-block:: console

    $ echo insecure-package==0.1.0 | safety check --stdin --json
    [
        [
            "insecure-package",
            "<0.2.0",
            "0.1.0",
            "This is an insecure package with lots of exploitable security vulnerabilities.",
            "25853"
        ]
    ]

Let's now write the operation to call ``safety`` via a subprocess.

**shouldi/safety.py**

.. literalinclude:: /../examples/shouldi/shouldi/safety.py

Write a test for it

**tests/test_safety.py**

.. literalinclude:: /../examples/shouldi/tests/test_safety.py

Run the tests

.. code-block:: console

    $ python3.7 setup.py test -s tests.test_safety

Bandit Operation
----------------

To get parsable output, we'll run with the ``-f json`` flag.

.. code-block:: console

    $ bandit -r -f json distributed-android-testing/
    {
      "metrics": {
        "_totals": {
          "CONFIDENCE.HIGH": 9.0,
          "CONFIDENCE.LOW": 0.0,
          "CONFIDENCE.MEDIUM": 3.0,
          "CONFIDENCE.UNDEFINED": 0.0,
          "SEVERITY.HIGH": 0.0,
          "SEVERITY.LOW": 10.0,
          "SEVERITY.MEDIUM": 2.0,
          "SEVERITY.UNDEFINED": 0.0,
          "loc": 5658,
          "nosec": 0
        }
      },
      "results": [
        {
          "code": "19         \"chmod 700 /tmp/docker_install.sh\",\n20         \"/tmp/docker_install.sh\",\n21         \"usermod -aG docker ${USER}\",\n22         \"service docker restart\"\n23     ]\n24     kwargs[\"sudo\"] = True\n25     ssh.run_all(command, **kwargs)\n",
          "filename": "distributed-android-testing/docker/docker.py",
          "issue_confidence": "MEDIUM",
          "issue_severity": "MEDIUM",
          "issue_text": "Probable insecure usage of temp file/directory.",
          "line_number": 20,
          "line_range": [
            18,
            19,
            20,
            21,
            22
          ],
          "more_info": "https://bandit.readthedocs.io/en/latest/plugins/b108_hardcoded_tmp_directory.html",
          "test_id": "B108",
          "test_name": "hardcoded_tmp_directory"
        },
        {
          "code": "22 PORT = 9898\n23 ADDRESS = \"0.0.0.0\"\n24 STREAM = True\n",
          "filename": "distributed-android-testing/docker/gitlab_webhooks/app.py",
          "issue_confidence": "MEDIUM",
          "issue_severity": "MEDIUM",
          "issue_text": "Possible binding to all interfaces.",
          "line_number": 23,
          "line_range": [
            23
          ],
          "more_info": "https://bandit.readthedocs.io/en/latest/plugins/b104_hardcoded_bind_all_interfaces.html",
          "test_id": "B104",
          "test_name": "hardcoded_bind_all_interfaces"
        }
      ]
    }


Let's now write the operation to call ``safety`` via a subprocess.

**shouldi/bandit.py**

.. literalinclude:: /../examples/shouldi/shouldi/bandit.py

Write a test for it

**tests/test_bandit.py**

.. literalinclude:: /../examples/shouldi/tests/test_bandit.py

Run the tests

.. code-block:: console

    $ python3.7 setup.py test -s tests.test_bandit

What's the Data Flow?
---------------------

So far ``shouldi`` uses two tools.

- ``bandit``

  - Which runs checks on the source code of a package to look for things like
    SQL injections

- ``safety``

  - Which checks if there are any open CVEs in a package

We're only planning on providing our tool with the package name. So we'll need
to find the package version to run ``safety``, and download the source code
of the package to run ``bandit``.

This is the directed graph that defines the dataflow of operations that make
up ``shouldi`` it shows us how all the operations we talked about above are
connected using other opertions which grabbed the package version and source
code from PyPi.

.. TODO Autogenerate this from the dataflow

.. image:: /images/shouldi-dataflow-processing.svg
    :alt: Diagram showing DataFlow for processing stage

The DataFlow above describes the following process:

- In the processing stage we run all our data collection operations

  - Our input is the ``package`` name

    - This will be given to us on the command line

  - Access the PyPi API and get the JSON describing the package information

  - Concurrently

    - Extract the version from the package information

      -  Run ``safety`` using the version and the package name

    - Extract the URL of the latest release from the package information

      - Use the URL to download and extract the package source to a directory

        - Run ``bandit`` using the package source directory

- In the cleanup stage we release resources created in the processing stage

  - Remove the package source directory

- In the output stage we run operations which select data generated in the
  processing stage and use that selected data as the output of the dataflow.

  - Run the ``get_single`` operation which selects data matching the definitions
    we care about.

PyPi Operations
---------------

Let's write an operation to grab the JSON information about a package.

**shouldi/pypi.py**

.. literalinclude:: /../examples/shouldi/shouldi/pypi.py
    :lines: 1-35

After we have the package information, we extract the version and URL where we
can get the source code.

**shouldi/pypi.py**

.. literalinclude:: /../examples/shouldi/shouldi/pypi.py
    :lines: 38-60

Once we have the URL, we download the package source and extract it to a
temporary directory.

**shouldi/pypi.py**

.. literalinclude:: /../examples/shouldi/shouldi/pypi.py
    :lines: 63-82

Finally, we make a ``cleanup`` operation to remove the directory once we're done
with it.

**shouldi/pypi.py**

.. literalinclude:: /../examples/shouldi/shouldi/pypi.py
    :lines: 85-90

Now we write tests for each operation.

**tests/test_pypi.py**

.. literalinclude:: /../examples/shouldi/tests/test_pypi.py

Run the tests

.. code-block:: console

    $ python3.7 setup.py test -s tests.test_pypi

CLI
---

Writing the CLI is as simple as importing our operations and having the memory
orchestrator run them. DFFML also provides a quick and dirty CLI abstraction
based on :py:mod:`argparse` which will speed things up.

**shouldi/cli.py**

.. literalinclude:: /../examples/shouldi/shouldi/cli.py

Let's test out the code in ``shouldi.cli`` before making it accessible via the
command line.

**tests/test_cli.py**

.. literalinclude:: /../examples/shouldi/tests/test_cli.py

Run the all the tests this time

.. code-block:: console

    $ python3.7 setup.py test

We want this to be usable as a command line utility, Python's
:py:mod:`setuptools` allows us to define console ``entry_points``. All we have
to do is tell :py:mod:`setuptools` what Python function we want it to call when
a user runs a given command line application. The name of our CLI is ``shouldi``
and the function we want to run is ``main`` in the ``ShouldI`` class which is in
the ``shouldi.cli`` module.

**setup.py**

.. literalinclude:: /../examples/shouldi/setup.py
    :lines: 17-18

Re-install the package via pip

.. code-block:: console

    $ python3.7 -m pip install -e .

Now we should be able to run our new tool via the CLI! (Provided your ``$PATH``
is set up correctly).

.. code-block:: console

    $ shouldi install dffml insecure-package
    dffml is okay to install
    Do not install insecure-package!
        safety_check_number_of_issues: 1
        bandit_output: {'CONFIDENCE.HIGH': 0.0, 'CONFIDENCE.LOW': 0.0, 'CONFIDENCE.MEDIUM': 0.0, 'CONFIDENCE.UNDEFINED': 0.0, 'SEVERITY.HIGH': 0.0, 'SEVERITY.LOW': 0.0, 'SEVERITY.MEDIUM': 0.0, 'SEVERITY.UNDEFINED': 0.0, 'loc': 100, 'nosec': 0, 'CONFIDENCE.HIGH_AND_SEVERITY.HIGH': 0}

.. _tutorials_operations_visualizing_the_dataflow:

Visualizing the DataFlow
------------------------

DataFlows can be visualized using `mermaidjs <https://mermaidjs.github.io/>`_.

.. note::

    Installing the ``dffml-config-yaml`` package will enable the
    ``-config yaml`` option. Allowing you to export to YAML instead of JSON.
    You can also convert between config file formats with the
    :ref:`cli_config_convert` command.

We first export the DataFlow to a config file on disk.

.. code-block:: console

    $ mkdir -p shouldi/deploy/df
    $ dffml service dev export -config json shouldi.cli:DATAFLOW \
      > shouldi/deploy/df/shouldi.json

We then create the mermaidjs digarm from the DataFlow. The ``-simple`` flag says
to only show connections between operations, don't show which inputs and outputs
are connected.

.. code-block:: console

    $ dffml service dev diagram -simple shouldi/deploy/df/shouldi.json
    graph TD
    subgraph a759a07029077edc5c37fea0326fa281[Processing Stage]
    style a759a07029077edc5c37fea0326fa281 fill:#afd388b5,stroke:#a4ca7a
    a55c24c0d1363ec4d3c9e20883f3c740[pypi_latest_package_version]
    d273c0a72c6acc57e33c2f7162fa7363[pypi_package_contents]
    83503ba9fe6c0f5649644d26e59c5590[pypi_package_json]
    00f7f4637f6f67120e83e75c78949806[pypi_package_url]
    9220cb5f5732d9e6dcc130a4908ddf92[run_bandit]
    88517e4cd0cae33deff50d987f2683fe[safety_check]
    end
    subgraph a4827add25f5c7d5895c5728b74e2beb[Cleanup Stage]
    style a4827add25f5c7d5895c5728b74e2beb fill:#afd388b5,stroke:#a4ca7a
    7ec0058800fd4bed6fb63633330588c7[cleanup_pypi_package]
    end
    subgraph 58ca4d24d2767176f196436c2890b926[Output Stage]
    style 58ca4d24d2767176f196436c2890b926 fill:#afd388b5,stroke:#a4ca7a
    b42e9e149e775202b18841f1f67061c4[get_single]
    end
    subgraph inputs[Inputs]
    style inputs fill:#f6dbf9,stroke:#a178ca
    d273c0a72c6acc57e33c2f7162fa7363 --> 7ec0058800fd4bed6fb63633330588c7
    d60584024f765273b6f41d6d36f8320c(get_single_spec)
    d60584024f765273b6f41d6d36f8320c --> b42e9e149e775202b18841f1f67061c4
    83503ba9fe6c0f5649644d26e59c5590 --> a55c24c0d1363ec4d3c9e20883f3c740
    00f7f4637f6f67120e83e75c78949806 --> d273c0a72c6acc57e33c2f7162fa7363
    314b1a20a4db6b3bf3f2627830da97a3(package)
    314b1a20a4db6b3bf3f2627830da97a3 --> 83503ba9fe6c0f5649644d26e59c5590
    83503ba9fe6c0f5649644d26e59c5590 --> 00f7f4637f6f67120e83e75c78949806
    d273c0a72c6acc57e33c2f7162fa7363 --> 9220cb5f5732d9e6dcc130a4908ddf92
    314b1a20a4db6b3bf3f2627830da97a3(package)
    314b1a20a4db6b3bf3f2627830da97a3 --> 88517e4cd0cae33deff50d987f2683fe
    a55c24c0d1363ec4d3c9e20883f3c740 --> 88517e4cd0cae33deff50d987f2683fe
    end

You can now copy that graph and paste it in the mermaidjs live editor:

- https://mermaidjs.github.io/mermaid-live-editor

It should render the following SVG showing how all the operations are connected.

.. image:: /images/shouldi-dataflow.svg
    :alt: Diagram showing DataFlow

GitLab will render mermaidjs diagrams found in markdown files. There is also a
sphinx plugin, and a command line utility.

.. _tutorials_operations_registering_opreations:

Registering Operations
----------------------

In order to make our operations visible to other plugins and packages using
DFFML, we need to register them with Python's ``entry_points`` system.

**setup.py**

.. literalinclude:: /../examples/shouldi/setup.py
    :lines: 17-28

Re-install the package via pip to make registrations take effect.

.. code-block:: console

    $ python3.7 -m pip install -e .

After you've registered the operations, services such as the
:doc:`/plugins/service/http/index` will have access to your operations.

To make sure your operations were registered, you can use the development
service's ``entrypoints list`` command. You should see the ``get_single``
operation we used to get our output as comming from ``dffml``. You'll also see
your own operations as coming from ``shouldi``.

.. code-block:: console

    $ dffml service dev entrypoints list dffml.operation
    associate = dffml.operation.output:Associate -> dffml 0.2.1 (/usr/local/lib/python3.7/dist-packages)
    dffml.mapping.create = dffml.operation.mapping:create_mapping -> dffml 0.2.1 (/usr/local/lib/python3.7/dist-packages)
    dffml.mapping.extract = dffml.operation.mapping:mapping_extract_value -> dffml 0.2.1 (/usr/local/lib/python3.7/dist-packages)
    get_single = dffml.operation.output:GetSingle -> dffml 0.2.1 (/usr/local/lib/python3.7/dist-packages)
    group_by = dffml.operation.output:GroupBy -> dffml 0.2.1 (/usr/local/lib/python3.7/dist-packages)
    cleanup_pypi_package = shouldi.pypi:cleanup_pypi_package -> shouldi 0.0.1 (/home/user/shouldi)
    pypi_latest_package_version = shouldi.pypi:pypi_latest_package_version -> shouldi 0.0.1 (/home/user/shouldi)
    pypi_package_contents = shouldi.pypi:pypi_package_contents -> shouldi 0.0.1 (/home/user/shouldi)
    pypi_package_json = shouldi.pypi:pypi_package_json -> shouldi 0.0.1 (/home/user/shouldi)
    pypi_package_url = shouldi.pypi:pypi_package_url -> shouldi 0.0.1 (/home/user/shouldi)
    run_bandit = shouldi.bandit:run_bandit -> shouldi 0.0.1 (/home/user/shouldi)
    safety_check = shouldi.safety:safety_check -> shouldi 0.0.1 (/home/user/shouldi)

The :doc:`/usage/dataflows` usage example will show you how to expose your new
meta static analysis tool over an HTTP interface.

.. code-block:: console

    $ curl -s \
      --header "Content-Type: application/json" \
      --request POST \
      --data '{"insecure-package": [{"value":"insecure-package","definition":"package"}]}' \
      http://localhost:8080/shouldi | python -m json.tool
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
