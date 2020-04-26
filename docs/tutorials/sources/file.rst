.. _new_file_type_source_tutorial:

Source for New file types
=========================

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

.. literalinclude:: ../../../dffml/source/ini.py
    :lines: 1-8

Here we are importing some common modules which will be required. The ``configparser``
module will be helpful in parsing INI files. The ``FileSource`` and ``MemorySource``
will be used as base class for our new Source. The config was imported to set the
configuration options for our new INISource. The entrypoint will be used to add the
entrypoint to our INISource. The ``Record`` is the dffml way of storing all the
data of the file(s).

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

Here we have added the entrypoint to INISource class as "ini". The INISource will inherit
from FileSource and MemorySource which provides read / write operations for file and
memory. Set the CONFIG variable to the INISourceConfig which we created earlier. Next we
will writing the load and dump methods for INISource.

Add load method
---------------

.. literalinclude:: ../../../dffml/source/ini.py
    :lines: 26-47
