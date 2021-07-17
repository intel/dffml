Command Line
============

Here are some useful command line invocations of the HTTP API, with explanation
of relevant flags.

.. warning::

    You should be sure to read the :doc:`security` docs! Some of these examples
    are insecure and only used to help you get up and running.

Quickstart
----------

This command starts the server without TLS (``-insecure``). It tells it to
listen on port 8080. It says that the server should be accessabel from any IP
address associated with the machine it's running on (``-addr 0.0.0.0``). It says
that should the server be accessed from JavaScript, don't worry about what
domain is hosting the JavaScript files attempting to access the server (``-cors
'*'``).

This is not the recommended way of running the server, but is probably what you
want when you're trying it out for the first time.

You can add these flags to any of the following commands to make the server
insecure, but easy for you to access for development purposes.

.. code-block:: console

    $ dffml service http server -insecure -cors '*' -addr 0.0.0.0 -port 8080

Models
------

To have the server start with models already configured and ready to be used for
training and prediction, use the ``-models`` flag.

.. code-block:: console

    $ dffml service http server \
        -models mymodel=slr \
        -model-mymodel-features X:float:1 \
        -model-mymodel-predict Y:float:1

Sources
-------

To have the server start with sources already configured and ready to be used
for record retrieval or updating, use the ``-sources`` flag.

.. code-block:: console

    $ dffml service http server \
        -sources mysource=csv \
        -source-mysource-filename training.csv

Scorer
------

To have the server start with scorer already configured and ready to be used
for getting the accuracy, use the ``-scorer`` flag.

.. code-block:: console

    $ dffml service http server \
        -scorers myscorer=mse

Static Content
--------------

If you have static HTML files or other content that you want to serve via the
HTTP server, you can do so via the ``-static`` flag. Content will be served from
the root ``/``. Dynamically registered paths for DataFlows take priority static
paths, and static paths take priority over Model and Source related paths.

.. code-block:: console

    $ dffml service http server -static .

Redirects
---------

You might want to have the HTTP service redirect one URL to another. You can do
this using the ``-redirect`` flag. Syntax is as follows

.. code-block::

    -redirect \
        METHOD_1 SOURCE_PATH_1 DESTINATION_PATH_1 \
        METHOD_2 SOURCE_PATH_2 DESTINATION_PATH_2 \
        METHOD_3 SOURCE_PATH_3 DESTINATION_PATH_3 \
        ...

Example of redirecting ``/`` to ``/index.html`` for GET requests

.. code-block::

    -redirect GET / /index.html

Redirect ``/`` to ``/index.html`` for GET requests and ``/signup`` to
``/mysignup`` for POST requests

.. code-block::

        -redirect \
            GET / /index.html \
            POST /signup /mysignup

Binding to a random port
------------------------

When writing tests you might often find yourself wanting the server to bind to
any free port.

Passing ``0`` for the port will have the HTTP service bind to any free port.

If the ``-portfile`` flag is given the HTTP service will write the port number
that was randomly chosen to the specified file as a string.

.. code-block::

        -port 0 -portfile portfile.int
