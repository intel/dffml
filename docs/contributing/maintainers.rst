Maintainer Docs
===============

These docs are for the maintainers of DFFML, if you're not a maintainer, you
won't find anything useful here, unless your just curious.

Adding A New Plugin
-------------------

When a new plugin is added we need to go manually upload it for the first time.

.. code-block:: console

    $ cd model/new_model
    $ python3.7 setup.py test
    $ rm -rf dist
    $ git clean -xdf
    $ python3.7 setup.py sdist
    $ twine upload dist/*

Once it's be uploaded, we go to PyPi and create an API key which will be used to
upload it via the automatic release at the end of ``run_plugin`` within the CI
script.

.. image:: /images/pypi-token-to-github-secret.gif

Finally, update the ``PYPI_TOKENS`` file in ``.github/workflows/testing.yml``.
Add a line for the plugin along with it's sceret.
