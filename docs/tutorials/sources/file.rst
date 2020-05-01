Simple source for new file types
================================

This tutorial will help you with implementing your own ``Source`` for new file
types. You may want to do this if you have some specific file formats from which
you want to load and save data from. Here we will go through implementing a source
for ``.ini`` file formats.

About INI files
---------------

An INI file is a configuration file used by Operating Systems and programs
to initialize program settings. It contains sections for settings and preferences
(delimited by a string in square brackets) with each section containing one
or more name and value parameters.

Import modules
--------------

.. code-block:: python

    from configparser import ConfigParser

    from dffml import config, entrypoint, Record, FileSource, MemorySource, parser_helper

Here we are importing some common modules which will be required. The ``configparser``
module will be helpful in parsing INI files. The ``FileSource`` and ``MemorySource``
will be used as base class for our new Source. The config was imported to set the
configuration options for our new INISource. The entrypoint will be used to add the
entrypoint to our INISource. A ``Record`` is a unique entry in a source.

Add configuration
-----------------

.. literalinclude:: ../../../dffml/source/ini.py
    :lines: 11-15

Here we will be writing the configuration options which will be avaliable for our
INISource. The INISourceConfig will be decorated by config. Here we have provided
three configuration options.

Create Source
-------------

.. literalinclude:: ../../../dffml/source/ini.py
    :lines: 18-24

Here we have added the entrypoint to INISource class as "ini". The new Source should inherit
from FileSource and MemorySource as it abstracts the saving and loading of files so that
we only have to implement the load_fd and dump_fd methods. It takes care of decompression
on load and re-compression on save if the files extension signifies that it's compressed.
We inherit from MemorySource because it implements the methods required by a
:py:class:`Source <dffml.source.source.BaseSourceContext>` provided that self.mem contains
Record objects.

Set the CONFIG variable to the INISourceConfig which we created earlier. Setting
the CONFIG variable is important because the instantiated version of CONFIG is accessible
as self.config.

Next we will writing the load and dump methods for INISource.

Add load method
---------------

.. literalinclude:: ../../../dffml/source/ini.py
    :lines: 26-47

This method will be used to load the data from the file(s). We will be reading data
from the file object (fileobj) and loading that data into memory (self.mem). Each
:py:class:`Record <dffml.record.Record>` instance consist of key (str type) of the
record and data (dict type), with data having a key ``features`` which stores all
the data for that record.

Going over the code, we have defined a coroutine with parameter fileobj, here
fileobj is the file object. we are reading from the fileobj file object. Each section of the
INI file is used as a Record, with the name of the section used as key for that Record.
Each section consist of name and value pair which we store it as a dict, under that Record
features key.

Add dump method
---------------

.. literalinclude:: ../../../dffml/source/ini.py
    :lines: 49-66

This method will be used to dump the data to the file. We will read data from memory
(self.mem) and save that data in file object (fileobj).

Going over the code, we have defined a coroutine with parameter fileobj, here
fileobj is the file object. We are going over each section name and its corresponding Record.
We are reading all the data from the memory (self.mem) and writing that data to our file
object (fileobj). Hence dumping all our data into file.
