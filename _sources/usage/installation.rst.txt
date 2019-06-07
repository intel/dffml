Installation
============

DFFML currently only supports Python 3.7. If your distribution's package manager
doesn't provide Python 3.7,
`pyenv <https://github.com/pyenv/pyenv#simple-python-version-management-pyenv>`_
is another good way to install it.

DFFML is available via pip.

.. code-block:: bash

    python3.7 -m pip install dffml

If you want to stay on the bleeding edge of bug fixes, etc. Install via git.

.. code-block:: bash

    python3.7 -m pip install git+https://github.com/intel/dffml

You can also install the Features for Git Version Control, and Models for
Tensorflow Library all at once.

.. code-block:: bash

    python3.7 -m pip install -U dffml[git,tensorflow]
