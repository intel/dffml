ffmpeg dataflow
===============

We'll be using ``ffmpeg`` which is a cli based utility for processing media files.
Make sure you `download and install <https://www.ffmpeg.org/download.html>`_ it.

Creating operations
-------------------

.. code-block:: console

    $ dffml service dev create operations ffmpeg
    $ cd ffmpeg

Remove the example files

.. code-block:: console

    $ rm ffmpeg/operations.py ffmpeg/definitions.py

.. note::
    All the code for this example is located under the
    `examples/ffmpeg <https://github.com/intel/dffml/blob/master/examples/ffmpeg/>`_
    directory of the DFFML source code.

Writing operations and definitions to convert videos files to gif by calling ``ffmpeg``

**ffmpeg/operations.py**

.. literalinclude:: /../examples/ffmpeg/ffmpeg/operations.py

**ffmpeg/definitions.py**

.. literalinclude:: /../examples/ffmpeg/ffmpeg/definitions.py

Change **setup.py** to include the new operation

.. literalinclude:: /../examples/ffmpeg/setup.py
    :lines: 12-16

Installing

.. code-block:: console

    $ pip install -e .

Testing the operation

**tests/test_operations.py**

.. literalinclude:: /../examples/ffmpeg/tests/test_operations.py

Copy a mp4 file named ``input.mp4`` to tests/,and run the test by

.. code-block:: console

    $ python3.7 setup.py test

verify that the operation is working by checking ``tests/output.gif``


