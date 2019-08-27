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

You can create a new python package and start implementing a new plugin for
DFFML right away with the ``create`` command of ``dev``.

.. code-block:: console

    $ dffml service dev create model cool-ml-model
    $ cd cool-ml-model
    $ python setup.py test

When you're done you can upload it to PyPi and it'll be ``pip`` installable so
that other DFFML users can use it in their code or via the CLI. If you don't
want to mess with uploading to ``PyPi``, you can install it from your git repo
(wherever it may be that you upload it to).

.. code-block:: console

    $ python -m pip install -U git+https://github.com/user/cool-ml-model

Make sure to look in ``setup.py`` and edit the ``entry_points`` to match
whatever you've edited. This way whatever you make will be usable by others
within the DFFML CLI (eventually HTTP API and others) as soon as they ``pip``
install your package, nothing else required.

dffml
-----

.. code-block:: console

    pip install dffml


dev
~~~

*Core*

Development utilities for hacking on DFFML itself

dffml_service_http
------------------

.. code-block:: console

    pip install dffml-service-http


http
~~~~

*Core*

HTTP interface to access DFFML API