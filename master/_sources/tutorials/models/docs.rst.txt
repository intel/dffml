.. _model_tutorial_docs:

Documenting a Model
===================

We can write the documentation and examples for our new model within the model
docstring. We should always include at least two examples so that others will
know how to use our model! We shoot for at least one command line example, and
one Python example. We can put the examples in restructured text format within
the class's docstring.

This tutorial is meant to go after the :ref:`model_tutorial_package` tutorial.

It's okay if you skipped to here though you can get up to speed by running the
following commands. These commands create the model package containing starter
code, change directory into the pacakge, install the package, and run the
setuptools ``egg_info`` hook to register the model with the ``entry_points``
system.

.. code-block:: console
    :test:

    $ dffml service dev create model dffml-model-myslr
    $ cd dffml-model-myslr
    $ python -m pip install -e .[dev]
    $ python setup.py egg_info

Python docstrings
-----------------

A docstring in Python is a comment immediately following a class or function
definition. Python will print out an object's docstring if the object is passed
to the :py:func:`help` function.

.. code-block:: console
    :test:

    $ python -c 'from dffml_model_myslr.myslr import MySLRModel; help(MySLRModel)'
    Help on class MySLRModel in module dffml_model_myslr.myslr:

    class MySLRModel(dffml.model.model.SimpleModel)
     |  MySLRModel(config: 'BaseConfig') -> None
     |
     |  Example Logistic Regression training one variable to predict another.
     |

The docstring goes right after our ``class`` definition. We prefix the block
comment ``"""`` with the character ``r`` which means that the block comment
will be treated as a "raw literal". For more information on raw literals see
https://docs.python.org/3/reference/lexical_analysis.html#string-and-bytes-literals.
In our case it essentially means that when we have a backslash it will be
treated as a backslash and not an escape character.

**dffml_model_myslr/myslr.py**

.. literalinclude:: /../dffml/skel/model/REPLACE_IMPORT_PACKAGE_NAME/myslr.py
    :lines: 66-68
    :linenos:
    :lineno-start: 66

Quick rST background
--------------------

When you see something with ``.. `` and ``::`` at the end that's called a
"directive". For example you'll see ``code-block`` and ``literalinclude`` which
are directives. Each string that follows ``::`` after a directive is known as an
"argument". On the lines immediately following a directive you may see one or
more of what's called an "option". These are strings with ``:`` on either end.

consoletest
-----------

We'll be using the consoletest Sphinx extension which adds extra options to
directives. Some options that you'll see are ``:test:`` and ``:filepath:``.
The full documentation for the consoletest Sphinx extension can be found here:
:doc:`/contributing/consoletest`.

The consoletest Sphinx extension will be used for
:ref:`model_tutorial_docs_testing_examples`. As we write our documentation we'll
keep in mind the functionality that consoletest provides. The goal is to write
documentation that a user would be able to copy paste file data and commands
from. The consoletest plugin will help us simulate the actions of the user.
Allowing us to write the same files and run the same commands we're asking the
developer to. Just as the developer will, the consoletest plugin will start
every test by creating an empty directory in which to do run it's test. Our
documentation is telling the developer what files to create within that
directory and what commands to run.

We use the ``:test:`` option on any directive that we want the consoletest
plugin to run. We'll use the ``:filepath:`` option whenever we want
to write data in a ``code-block`` to a file within the test environment's
temporary directory. When the ``literalinclude`` directive is used to display
contents of a file, we can also have the contents that are being displayed
copied into a file of a given name within the test environment by using the
``:filepath:`` option.

Sometimes you may just want to show a ``code-block`` or a ``literalinclude``
that consoletest shouldn't run. Just leave off the ``:test:`` option in these
situations.

.. _model_tutorial_docs_example_datasets:

Example Datasets
----------------

We can include text data to be written to files within ``code-block``
directives. You may want to download data from the internet instead. Running a
command via ``code-block:: console`` which you'll see an example of shortly is a
good way to do that.

We usually start by telling the user to create the training and test datasets.
We always try to make it clear to the user what file they should be writing it
by putting the filename in bold above the file contents.

**dffml_model_myslr/myslr.py**

.. literalinclude:: /../dffml/skel/model/REPLACE_IMPORT_PACKAGE_NAME/myslr.py
    :language: rst
    :lines: 71-97
    :linenos:
    :lineno-start: 71

Example CLI Commands
--------------------

After the user has saved the training and test dataset files. We'll give then
the command line example usage. We're going to document how to train the model,
assess it's accuracy, and use it for prediction.

When there is a way that a ``code-block`` should be highlighted, we can give it
as an argument. ``console``, is the way that code examples that users should run
in the console should be highlighted. There is no proper way to highlight a
``.csv`` file, which is why we didn't talk about highlighting in the
:ref:`model_tutorial_docs_example_datasets` section.

**dffml_model_myslr/myslr.py**

.. literalinclude:: /../dffml/skel/model/REPLACE_IMPORT_PACKAGE_NAME/myslr.py
    :language: rst
    :lines: 99-163
    :linenos:
    :lineno-start: 99

Example Python Usage
--------------------

Try to include as much of the examples inline as possible. However, when it
comes time to include a Python file in an example it's best to leave it as a
separate file and use ``literalinclude`` to display the contents. We do this
because the auto formatter, `black <https://github.com/psf/black>`_, can only
format Python files. It can't format examples within rST within a docstring.

**dffml_model_myslr/myslr.py**

.. literalinclude:: /../dffml/skel/model/REPLACE_IMPORT_PACKAGE_NAME/myslr.py
    :language: rst
    :lines: 164-171
    :linenos:
    :lineno-start: 164

By specifying the ``:filepath:`` we copied the contents of the Python example
to the test environment's directory. The last thing we need to do is run the
Python example and show what it's output would be. Then end the docstring with
another ``"""```.

**dffml_model_myslr/myslr.py**

.. literalinclude:: /../dffml/skel/model/REPLACE_IMPORT_PACKAGE_NAME/myslr.py
    :language: rst
    :lines: 173-178
    :linenos:
    :lineno-start: 172

.. _model_tutorial_docs_testing_examples:

Testing Examples
----------------

Using the
`consoletest <https://github.com/intel/dffml/tree/master/dffml/util/testing/consoletest>`_
module we can test the ``code-block`` sections within the docstring. DFFML has a
:py:func:`run_consoletest <dffml.util.testing.docs.run_consoletest>` function we
will be using.

We have an integration test file which will use
:py:func:`run_consoletest <dffml.util.testing.docs.run_consoletest>`
to test the model's docstring.

**tests/test_integration.py**

.. code-block:: python
    :test:
    :filepath: tests/test_integration.py

    from dffml import AsyncTestCase, run_consoletest

    from dffml_model_myslr.myslr import MySLRModel


    class TestIntegrationMySLRModel(AsyncTestCase):
        async def test_docstring(self):
            await run_consoletest(MySLRModel)

We can run the test using the ``unittest`` module. The create command gave us
both unit tests and integration tests. We want to only run the integration test
right now (``tests.test_integration``).

.. TODO There is something wrong with consoletest and how it runs this final
   command. They myslr model is raising an EntrypointNotFound exception.

.. code-block:: console

    $ python -m unittest -v tests.test_integration

.. note::

    This tutorial will be updated to show how to build a documentation website
    just like this one which will display an HTML version of restructured text.
