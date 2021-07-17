Documentation
=============

Before building the docs, you'll want to have pandocs as well as all of the
official plugins installed. See :ref:`dev_env_install_official_plugins`.
For most Linux distros, you can install pandocs by

.. code-block:: console

    $ sudo apt-get install pandoc

For alternative ways to install, refer to
`pandocs documentation <https://pandoc.org/installing.html>`_.

After you have installed the required plugins, you can build the docs by running the
script.

.. code-block:: console

    $ dffml service dev docs

Python's built in HTTP server is useful for viewing the documentation.

.. code-block:: console

    $ python3 -m http.server --directory pages/ 7000

Examples
--------

Most of the codebase uses the ``async`` and ``await`` keywords. As such, almost
every example block will need to define code that use those keywords within a
main coroutine (function defined with ``async def``). We'll then run that
coroutine with the :py:func:`asyncio.run` function.

Example documentation is expected to follow the ``black`` formatters code style.
``black`` does not yet auto-format example code, so you may want to write the
code in a separate file and format it there before copying it into the example.

.. code-block:: python

    async def sadd(self, context_handle_string, *args: Input):
        """
        Shorthand for creating a MemoryInputSet with a StringInputSetContext.

        >>> async def main():
        ...     async with MemoryOrchestrator.withconfig({}) as orchestrator:
        ...         async with orchestrator(DataFlow.auto()) as octx:
        ...             await octx.ictx.sadd("Hi")
        >>> asyncio.run(main())
        """

Setup for Example Code
----------------------

Everything the example code needs must be setup within the
``tests/test_doctests.py`` file. It imports all of the files within ``dffml/``
and creates a ``unittest.TestCase`` for each class or function with examples.
It also creates a temporary directory for the tests to run in.

See that file for more details on doing extra setup and tear down for specific
tests.

Doctests
--------

To run all the examples

.. code-block:: console

    $ python3 -m unittest tests.test_docstrings

To run a specific example, determine python path to class or function, remove
``dffml.`` and change rest of ``.`` to ``_``.

.. code-block:: console

    $ python3 -m unittest tests.test_docstrings.util_asynctestcase_AsyncTestCase
