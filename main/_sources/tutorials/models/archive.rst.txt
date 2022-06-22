Using Archives to Store Models
==============================

All the models listed on the :doc:`/plugins/dffml_model` page can be
stored as and loaded from archives, simply by setting the location property  
to any supported archive format file. 

Currently we support `tar` and `zip` formats of archives which can be paired with 
`gzip`, `lzma` and `bzip2` compression.

**archive.py**

.. literalinclude:: /../examples/tutorials/models/archive/archive.py
    :test:

.. code-block:: console
    :test:

    $ python archive.py