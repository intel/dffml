Simple source for new file types
================================

This tutorial will help you with implementing your own ``Source`` for new file
types. You may want to do this if you have some specific file formats from which
you want to load and save data from.

Here we will go through implementing a source for ``.ini`` file formats.

Create the Package
------------------

To create a new source we first create a new Python package. DFFML has a script
to do it for you.

.. code-block:: console
    :test:

    $ dffml service dev create source dffml-source-ini
    $ cd dffml-source-ini

We will start writing our source in ./dffml_source_ini/misc.py

About INI files
---------------

An INI file is a configuration file used by Operating Systems and programs
to initialize program settings. It contains sections for settings and preferences
(delimited by a string in square brackets) with each section containing one
or more name and value parameters.

Import modules
--------------

**dffml_source_ini/misc.py**

.. code-block:: python
    :test:
    :filepath: dffml_source_ini/misc.py

    from configparser import ConfigParser

    from dffml import config, entrypoint, Record, FileSource, MemorySource, parser_helper

Here we are importing some common modules which will be required. The ``configparser``
module will be helpful in parsing INI files. The ``FileSource`` and ``MemorySource``
will be used as base class for our new Source. The config was imported to set the
configuration options for our new INISource. The entrypoint will be used to add the
entrypoint to our INISource. A ``Record`` is a unique entry in a source.

Add configuration
-----------------

**dffml_source_ini/misc.py**

.. literalinclude:: /../dffml/source/ini.py
    :test:
    :filepath: dffml_source_ini/misc.py
    :lines: 11-15

Here we will be writing the configuration options which will be avaliable for our
INISource. The INISourceConfig will be decorated by config. Here we have provided
three configuration options.

Create Source
-------------

**dffml_source_ini/misc.py**

.. literalinclude:: /../dffml/source/ini.py
    :test:
    :filepath: dffml_source_ini/misc.py
    :lines: 18-24

Here we have added the entrypoint to INISource class as "ini". Do note that "ini" source
already exist in dffml list of sources, so you may want to call your own source as "myini".
The new Source should inherit from FileSource and MemorySource as it abstracts the saving
and loading of files so that we only have to implement the load_fd and dump_fd methods.
It takes care of decompression on load and re-compression on save if the files extension
signifies that it's compressed. We inherit from MemorySource because it implements the
methods required by a :py:class:`Source <dffml.source.source.BaseSourceContext>` provided
that self.mem contains Record objects.

Set the CONFIG variable to the INISourceConfig which we created earlier. Setting
the CONFIG variable is important because the instantiated version of CONFIG is accessible
as self.config.

Next we will writing the load and dump methods for INISource.

Add load method
---------------

**dffml_source_ini/misc.py**

.. literalinclude:: /../dffml/source/ini.py
    :test:
    :filepath: dffml_source_ini/misc.py
    :lines: 26-47

This method will be used to load the data from the file(s). We will be reading data
from the file object (fileobj) and loading that data into memory (self.mem). Each
:py:class:`Record <dffml.record.Record>` instance consist of key (str type) of the
record and data (dict type), with data having a key ``features`` which stores all
the data for that record.

Going over the code, we have defined a coroutine with parameter fileobj, here
fileobj is the file object. we are reading from the fileobj file object. Each section of the
INI file is used as a Record, with the name of the section used as key for that Record.
Each section consists of key value pairs stored as a dict. We're going to treat
this data as the feature data for each Record. To do so we pass the data as
the value for the ``features`` key under the ``data`` keyword argument when
creating a new Record.

Add dump method
---------------

**dffml_source_ini/misc.py**

.. literalinclude:: /../dffml/source/ini.py
    :test:
    :filepath: dffml_source_ini/misc.py
    :lines: 49-66

This method will be used to dump the data to the file. We will read data from memory
(self.mem) and save that data in file object (fileobj).

Going over the code, we have defined a coroutine with parameter fileobj, here
fileobj is the file object. We are going over each section name and its corresponding Record.
We are reading all the data from the memory (self.mem) and writing that data to our file
object (fileobj). Hence dumping all our data into file.

Add Tests
---------

**tests/test_source.py**

.. code-block:: python
    :test:
    :filepath: tests/test_source.py

    import os
    from tempfile import TemporaryDirectory

    from dffml import Record, load, save, AsyncTestCase

    from dffml_source_ini.misc import INISource

Before writing the test we need to import some modules which we will be using. We need
to import the source file which we created earlier. We need to import ``save`` and
``load`` from high_level. save method will be used to save the records to the source and
load will be used to yield records from a source. AsyncTestCase will be used to run our
test methods as coroutines in default event loop.

**tests/test_source.py**

.. literalinclude:: /../tests/source/test_ini.py
    :test:
    :filepath: tests/test_source.py
    :lines: 10-30

To test the working of the INISource created we will create a class TestINISource, since
we are using the unittest testing framework. The TestINISource will inherit from AsyncTestCase
so that it can be run as a coroutine in the default event loop. In the test method we will
create a TemporaryDirectory which will contain our `.ini` file.

We will create an instance of our INISource with configuration options. Next we will use
the save method to save some records to the source. Do not forget to await the save method
as it is a coroutine. Next we will use the load method to yield records from the source.
load method will return AsyncIterator[Record] type object. Lastly, We need to check that
the records we saved is the same record which gets loaded.

Run the tests
-------------

To run the tests

.. code-block:: console
    :test:

    $ python -m unittest discover -v

This will look into the file test_source.py and run all the tests.

Add the entrypoint
------------------

To register your source under dffml entrypoint you need to make sure you have a
``shorthand`` equals ``python.path.to:Class`` line in the ``entry_points.txt``
file.

**entry_points.txt**

.. code-block:: ini
    :test:
    :overwrite:
    :filepath: entry_points.txt

    [dffml.source]
    myini = dffml_source_ini.misc:INISource

This will add the newly created source to the dffml entrypoints and hence can
also be used in CLI.

Install your package
--------------------

To install your new source run

.. code-block:: console
    :test:

    $ python -m pip install -e .[dev]

CLI Usage
---------

Create a ``.ini`` file with some record data in it.

**data.ini**

.. code-block:: ini
    :test:
    :filepath: data.ini

    [dffml]
    third_party = yes
    maintained = true

    [python]
    third_party = no
    maintained = true

To use your newly created source in CLI, try listing some records.

.. code-block:: console
    :test:

    $ dffml list records -sources data=myini -source-filename data.ini
    [
        {
            "extra": {},
            "features": {
                "maintained": true,
                "third_party": true
            },
            "key": "dffml"
        },
        {
            "extra": {},
            "features": {
                "maintained": true,
                "third_party": false
            },
            "key": "python"
        }
    ]
