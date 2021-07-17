HTTP API
========

This project provides access to ``dffml`` APIs via an HTTP interface.

It exposes a REST-like API which mimics that of ``dffml``'s command line
interface (CLI) and usage as Python module.

You can install the HTTP API service via ``pip``

.. code-block:: console

    $ python3 -m pip install dffml-service-http

If you want to install the latest development version, clone dffml and install
from you can use ``git+``

.. code-block:: console

    $ git clone https://github.com/intel/dffml
    $ python3 -m pip install -e dffml/service/http[dev]

If you want to run this securely you can see :doc:`security`.

For an **insecure** setup, which might be easier for you to get started with for
development purposes. You can run the service via DFFML ``service`` command.

The default port is ``8080``. You can change this with the ``-port`` flag. Also,
by default the service is only accessible via ``127.0.0.1`` or ``localhost``. To
allow connections from machines other than the machine running the HTTP API, add
the ``-addr 0.0.0.0``. This tells the server to allow connections coming from
anywhere on your network. If your running this on a public server, your network
is the internet, which is dangerous. Also since your web app you're using for
development is probably hosted on another port, you'll need the ``cors`` flag.

.. warning::

    By no means should you use the following command in a production
    environment! You should instead see the :doc:`security` docs!

.. code-block:: console

    $ dffml service http server -insecure -cors '*' -addr 0.0.0.0 -port 8080

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    cli
    dataflow
    api
    security
    javascript
    python
