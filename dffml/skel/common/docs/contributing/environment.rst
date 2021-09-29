Development Environment Set Up
==============================

To start contributing code to you'll need to download install in development
mode.

First you'll want to clone the code with ``git``.

.. code-block:: console

    $ git clone https://github.com/REPLACE_ORG_NAME/REPLACE_PACKAGE_NAME

Change directory into the downloaded source repo.

.. code-block:: console

    $ cd REPLACE_PACKAGE_NAME

Virtual environments give you a little more isolation than installing to your
home directory. The disadvantage is you have to ``activate`` them every time you
want to use the packages you've installed in them.

Python 3 should have ``virtualenv`` built in as ``venv`` if not you can just
install ``virtualenv`` and use that. If you're on a Debian based distro you may
need to install the ``python3-venv`` package first (``apt-get install -y
python3-venv``).

Create the virtual environment.

.. code-block:: console

    $ python3 -m venv .venv

Activate it (on Linux / OSX / UNIX variants)

.. code-block:: console

    $ . .venv/bin/activate

Activate it (on Windows)

.. code-block:: console

    $ .\.venv\Scripts\activate

Before installing Python packages, we should update Python's package
installation tools to their latest versions.

.. code-block:: console

    $ python3 -m pip install -U pip
    $ python3 -m pip install -U setuptools wheel

Install our package in development mode.

``[dev]`` tells ``pip`` to install the dependencies you'll need to do
development work (such as documentation generation utilities). These
dependencies are defined within the ``options.extras_require`` section of the
``setup.cfg`` file.

.. code-block:: console

    $ python3 -m pip install -e .[dev]

The package is now installed and can be the Python ``import`` instruction will
work to import the package from anywhere on the system.
