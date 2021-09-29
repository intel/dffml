Documentation
=============

After you have installed the project in development mode, you can build the docs
by running ``sphinx-build``.

.. code-block:: console

    $ sphinx-build -b html docs/ built_html_docs/

Python's built in HTTP server is useful for viewing the documentation.

.. code-block:: console

    $ python3 -m http.server --directory built_html_docs/ 8080
