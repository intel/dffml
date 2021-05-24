Notebooks
=========

Code Formatting
---------------

After having written a notebook, it should be made sure that the code is
in the right format, ie. the ``black`` formatters code style. A
convenient way to achieve this in ``jupyter notebook`` is to install the
`jupyter-black extension <https://github.com/drillan/jupyter-black>`_.

Testing
-------

Once you've made an example notebook, the code inside the notebook will need
to be tested before it can be merged into the codebase. Notebooks cannot be
tested in the typical manner, as a notebook file consists of more than just the code.
To test notebooks, DFFML utilizes 
`testbook <https://testbook.readthedocs.io/en/latest/usage/index.html>`_.

``testbook`` provides different ways to access, unittest and mock the code inside
a notebook. Following is an example of how `testbook` can be used to test a notebook,
in this case,
:doc:`../examples/notebooks/moving_between_models`

.. literalinclude:: /../tests/notebooks/test_moving_between_models.py

Documentation
-------------

Notebooks are added to the documentation by utilizing ``nbsphinx`` and
``nbsphinx-link``. ``nbsphinx`` only lets you add notebooks that are
present in the same directory to the documentation. To overcome this,
``nbsphinx-link`` is used, which allows you to create a symblic link to
notebooks in other directories.

You can create the link to a notebook in a file with extention ``.nblink`` as follows

.. literalinclude:: /examples/notebooks/moving_between_models.nblink

After the link has been created, the ``nblink`` file is simply added to a toctree
to be displayed in the documentation

.. code-block:: text

    .. toctree::
        :maxdepth: 2

        moving_between_models
