Documentation
=============

You'll want to have all of the official plugins installed when generating the
documentation. See :ref:`dev_env_install_official_plugins`.

To build, run the docs script.

.. code-block:: console

    $ ./scripts/docs.sh

Python's built in HTTP server is useful for viewing the documentation.

.. code-block:: console

    $ python3.7 -m http.server --directory pages/ 7000

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

Everything the example code needs must be setup by the
``docs/doctest_header.py`` file. It contains the ``import`` statements and
creates a temporary directory for the tests to run in.

.. note::

  The ``.. testsetup::`` directive seemed to be crashing Sphinx, so be aware if
  you attempt to use it.

Doctests
--------

All the examples are tested by the Sphinx doctest extension. To test all of the
examples, run the doctest script.

.. code-block:: console

    $ ./scripts/doctest.sh
    Running Sphinx v2.4.3
    making output directory... done
    loading intersphinx inventory from https://docs.python.org/3/objects.inv...
    building [mo]: targets for 0 po files that are out of date
    building [doctest]: targets for 58 source files that are out of date
    updating environment: [new config] 58 added, 0 changed, 0 removed
    reading sources... [100%] usage/mnist

    looking for now-outdated files... none found
    pickling environment... done
    checking consistency... done
    running tests...

    Document: api/high_level
    ------------------------
    1 items passed all tests:
       3 tests in default
    3 tests in 1 items.
    3 passed and 0 failed.
    Test passed.

    Document: api/base
    ------------------
    1 items passed all tests:
       4 tests in default
    4 tests in 1 items.
    4 passed and 0 failed.
    Test passed.

    Document: api/df/memory
    -----------------------
    1 items passed all tests:
       4 tests in default
    4 tests in 1 items.
    4 passed and 0 failed.
    Test passed.

    Document: api/util/net
    ----------------------
    1 items passed all tests:
       4 tests in default
    4 tests in 1 items.
    4 passed and 0 failed.
    Test passed.

    Doctest summary
    ===============
       15 tests
        0 failures in tests
        0 failures in setup code
        0 failures in cleanup code
    build succeeded, 4 warnings.

    Testing of doctests in the sources finished, look at the results in ../../home/user/Documents/python/dffml/doctest/output.txt.
