Services
========

Services could be anything that wants to associate itself with the DFFML API.

For instance there is a HTTP service in the works that will allow access to
DFFML APIs similarly to the way the CLI does, over an HTTP interface.

Services could also be any helper utilities, such as the ``dev`` service. Which
helps developers who want to create new Models, Sources, Operations, or
Services. It also helps developers hack on DFFML itself.

.. code-block:: console

    $ dffml service -h

dffml
-----

.. code-block:: console

    pip install dffml


dev
~~~

*Official*

Development utilities for hacking on DFFML itself

dffml_service_http
------------------

.. code-block:: console

    pip install dffml-service-http


http
~~~~

*Official*

HTTP interface to access DFFML API.