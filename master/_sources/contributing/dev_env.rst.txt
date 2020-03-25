Getting Set Up To Work On DFFML
===============================

.. contents:: Development Environment Setup Methods

To start contributing code to DFFML you'll need to download and install it in
development mode.

.. note::

    If you don't want to deal with installing Python 3.7 or getting your
    development environment setup locally on your machine (since that can be a
    pain sometimes), there's an online IDE called GitPod that seems pretty
    useful which you can also use to get started working with on DFFML right
    away.

    .. image:: https://gitpod.io/button/open-in-gitpod.svg
       :target: https://gitpod.io/#https://github.com/intel/dffml

Before you install DFFML in development mode be sure to uninstall it! Python
will use the version installed from PyPi rather than you're development version
unless you uninstall it first!

.. code-block:: console

    $ python3.7 -m pip uninstall dffml

Once you're sure DFFML is not installed on your system, install it in
development mode.

Installing to your home directory is the recommended installation method. To do
this we use the ``--prefix=~/.local`` flag.

.. note::

    ``pip`` sometimes gets confused about the ``--user`` flag (and will blow up
    in your face if you try to pass it). So we use the ``--prefix=~/.local``
    flag, which has the same effect but should always work.

``[dev]`` tells ``pip`` to install the dependencies you'll need to do
development work on DFFML (such as documentation generation utilities).

.. code-block:: console

    $ git clone https://github.com/intel/dffml
    $ cd dffml
    $ python3.7 -m pip install --prefix=~/.local -e .[dev]

Verify you can use ``dffml`` from the command line.

.. code-block:: console

    $ dffml version
    dffml version 0.3.1 (devmode: /wherever/you/cloned/dffml)

If you see ``dffml`` in ``~/.local/bin`` but you can't run it on the command
line, then you'll need to add that directory to your ``PATH`` environment
variable. This might need to be in ``~/.bashrc``, ``~/.bash_profile``, or
``~/.profile``, depending on your flavor of UNIX or Linux Distro.

.. code-block:: console

    $ echo 'export PATH="${HOME}/.local/bin:${PATH}"' >> ~/.bashrc
    $ source ~/.bashrc

If you are working on any of the plugins to DFFML maintained within it's
repository make sure to install those in development mode as well.

For example, to install the TensorFlow models

.. code-block:: console

    $ python3.7 -m pip install --prefix=~/.local -e model/tensorflow

.. _dev_env_install_official_plugins:

Installing Plugins In Development Mode
--------------------------------------

To install all the plugins in development mode use the development service's
install command.

.. warning::

    The ``-user`` flag tells pip to install to your home directory
    (in ``~/.local``). Therefore, do NOT run install ``-user`` with ``sudo``.

.. code-block:: console

    $ dffml service dev install -user

Virtual Environment
-------------------

Virtual environments give you a little more isolation than installing to your
home directory. The disadvantage is you have to ``activate`` them every time you
want to use the packages you've installed in them.

Python 3 should have ``virtualenv`` built in as ``venv`` if not you can just
install ``virtualenv`` and use that.

Create the virtual environment.

.. code-block:: console

    $ python3.7 -m venv .venv


Activate it.

.. code-block:: console

    $ . .venv/bin/activate

Install the packages in development mode.

.. code-block:: console

    $ pip install -U setuptools
    $ pip install -e .[dev]
    $ dffml service dev install

Containerized Development Environment
-------------------------------------

Development environments can be a pain to setup, or can get messed up for
unknown reasons sometimes. When all else fails, a clean container usually does
the trick.

- ``run``

  - Start a new container.

- ``--rm``

  - Remove the container when you exit.

- ``-ti``

  - Run the container as an interactive terminal session.

- ``-u $(id -u):$(id -g)``

  - Preserve your file permissions and user to be the same in the container as
    on your host system. (Instead of making you root, if you leave this off
    you'll have to chown all your files back to your regular user when you exit
    the container, I do not recommend being root in the container).

- ``-v $PWD:/usr/src/dffml``

  - Use the directory you're currently in (should be the root of the dffml repo)
    as the /usr/src/dffml directory within the container.

- ``-w /usr/src/dffml``

  - Make the current working directory of the container /usr/src/dffml when
    started.

- ``--entrypoint /bin/bash``

  - Run bash instead of the Python interpreter when you start the container.

- ``python:3.7``

  - Download an run the docker image for running Python 3.7 applications.

.. code-block:: console

    $ sudo docker run --rm -ti -u $(id -u):$(id -g) \
      -v $PWD:/usr/src/dffml -w /usr/src/dffml --entrypoint /bin/bash python:3.7
    I have no name!@33ba998c91b3:/usr/src/dffml$ `# You are now in the container, your prompt will look something like this`

You can then setup a fake home directory for yourself in ``.venv`` and install
all the packages in development mode.

.. code-block:: console

    $ rm -rf .venv/
    $ mkdir -p .venv
    $ export HOME="${PWD}/.venv"
    $ export PATH="${HOME}/.local/bin:${PATH}"
    $ pip install --user -U pip setuptools
    $ pip install --prefix=~/.local -e .[dev]
    $ dffml service dev install -user

If things ever get messed up again, just wipe out ``.venv`` and re-install the
packages. Otherwise, you can just start the container again using the same
command, and export ``HOME`` and ``PATH`` to get back to your working
environment.

I'd recommend editing the files in another terminal window if your vimto that.
Or just using your favorite IDE as usual will work fine (since you mounted the
source repo in as a volume). Also, run ``git`` from outside the container.
