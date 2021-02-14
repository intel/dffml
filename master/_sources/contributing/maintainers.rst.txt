Maintainer Docs
===============

These docs are for the maintainers of DFFML, if you're not a maintainer, you
won't find anything useful here, unless your just curious.

Adding A New Plugin
-------------------

When a new plugin is added we need to go manually upload it for the first time.

.. code-block:: console

    $ cd model/new_model
    $ python3 setup.py test
    $ rm -rf dist
    $ git clean -xdf
    $ python3 setup.py sdist
    $ twine upload dist/*

Once it's be uploaded, we go to PyPi and create an API key which will be used to
upload it via the automatic release at the end of ``run_plugin`` within the CI
script.

.. image:: /images/pypi-token-to-github-secret.gif

Finally, update the ``PYPI_TOKENS`` file in ``.github/workflows/testing.yml``.
Add a line for the plugin along with it's sceret.

Doing a Release
---------------

- Increment the version number of each package

- Increment the version number of the main package in the dependency list of
  each package

.. warning::

    Some plugins depend on each other. For example
    ``model/tensorflow_hub`` depends on ``model/tensorflow``. Its important to
    update the version of ``dffml-model-tensorflow`` in
    ``model/tensorflow_hub``.

    To get a list of all the plugins that depend on each other. Run the
    following set of grep commands.

    .. code-block:: console

        $ git grep dffml- | grep setup | grep '=.*\..*\.'
        examples/shouldi/setup_common.py:        ["dffml-feature-git>=0.2.7"]
        model/tensorflow_hub/setup.py:        ["dffml-model-tensorflow>=0.2.7"]
        operations/deploy/setup_common.py:        ["dffml-feature-git>=0.2.7"]

- Modify ``CHANGELOG.md`` to replace the ``Unreleased`` section header with the
  new version and the date

- Commit the new version

- Tag a release

.. code-block:: console

    $ dffml service dev bump packages 0.0.1 -log debug
    $ dffml service dev bump main
    $ sed -i "s/Unreleased]/$(dffml service dev setuppy version dffml/version.py)] - $(date +%F)/" CHANGELOG.md
    $ git c "release: Version $(dffml service dev setuppy version dffml/version.py)"
    $ git tag $(dffml service dev setuppy version dffml/version.py)
