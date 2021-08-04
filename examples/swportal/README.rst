Software Portal
===============

Example of using DFFML to create a web app to discover information about
software.

All the code for this example project is located under the
`examples/swportal <https://github.com/intel/dffml/blob/master/examples/swportal/>`_
directory of the DFFML source code.

Setup
-----

Install dependencies

.. code-block:: console
    :test:

    $ python -m pip install -U pip setuptools wheel
    $ python -m pip install -U dffml dffml-service-http dffml-config-yaml
    $ python -m pip install -r requirements.txt

Usage
-----

Run the http service and navigate to http://localhost:8080/

.. warning::

    The ``-insecure`` flag is only being used here to speed up this
    tutorial. See documentation on HTTP API
    :doc:`/plugins/service/http/security` for more information.

.. code-block:: console
    :test:
    :daemon: 8080

    $ dffml service http server \
        -port 8080 \
        -mc-atomic \
        -mc-config projects \
        -static html-client \
        -redirect GET / /index.html \
        -log debug \
        -insecure

Query all projects

.. code-block:: console
    :test:
    :replace: cmds[0][-1] = cmds[0][-1].replace("8080", str(ctx["HTTP_SERVER"]["8080"]))

    $ curl -sf http://localhost:8080/projects

Get a specific project. This triggers a project's DataFlow to run.

.. code-block:: console
    :test:
    :replace: cmds[0][-1] = cmds[0][-1].replace("8080", str(ctx["HTTP_SERVER"]["8080"]))

    $ curl -sf http://localhost:8080/projects/72b4720a-a547-4ef7-9729-dbbe3265ddaa

Structure
---------

- The codebase for the client is in `html-client/`

- The DataFlows for each project are in `projects/`

  - Custom operations reside in the `operations/` directory

  - Dependencies are listed in the top level `requirements.txt` file.

HTML Client
+++++++++++

The website displayed to clients is all vanila HTML, CSS, and JavaScript.

Projects
++++++++

Each project has a DataFlow which describes how data for the project should be
collected. Static data can be added directly to the dataflow file. When
gernating data dynamically is required, code can be added to `operations/`.

Notes
-----

Run a single project's DataFlow from the command line

.. code-block:: console
    :test:

    $ dffml dataflow run single \
        -dataflow projects/df/b7cf5596-d427-4ae3-9e95-44be879eae73.yaml \
        -log debug
