Command Line
============

Here are some useful command line invocations of the HTTP API, with explanation
of relevant flags.

.. warning::
    You should be sure to read the :doc:`security` docs! Some of these examples
    are insecure and just used to help you get up and running.

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
training, accuracy assessment, or prediction, use the ``-models`` flag.

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
