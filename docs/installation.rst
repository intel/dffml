Installation
============

DFFML currently **supports Python 3.7 and 3.8 on Linux**. If your distribution's
package manager doesn't provide Python 3.7 or 3.8,
`pyenv <https://github.com/pyenv/pyenv#simple-python-version-management-pyenv>`_
is another good way to install it. You could also use the docker container.

**Windows and MacOS are not officially supported yet**. Support varies by which
plugins you install. We do not currently have a list of what is supported and
what is not supported on those OSs. Most things should work. However, until we
are testing for everything we won't declare them to be officially supported.
Please create issues for any problems you encounter.

First make sure you have the latest versions of ``pip``, ``setuptools``, and
``wheel``. Some ML libraries require them to be up-to-date.

.. tabs::

    .. group-tab:: Linux and MacOS

        .. code-block:: console
            :test:

            $ python -m pip install -U pip setuptools wheel

    .. group-tab:: Windows

        On Windows you may want to first create a virtual environment to avoid
        any permissions issues when running ``pip install``.

        .. code-block:: console

            C:\Users\username> python -m venv .venv
            C:\Users\username> .venv\Scripts\activate
            (.venv) C:\Users\username> python -m pip install -U pip setuptools wheel

DFFML is available via pip. You can install it as you would any other Python
package.

.. tabs::

    .. group-tab:: Linux and MacOS

        .. code-block:: console
            :test:

            $ python3 -m pip install -U dffml

    .. group-tab:: Windows

        .. code-block:: console

            (.venv) C:\Users\username> python -m pip install -U dffml

.. warning::

    Make sure that if pip is complaining that directories are not in your
    ``PATH``, that you add those directories to your ``PATH`` environment
    variable!.

You should now be able to run the ``dffml version`` command. If you have issues
adding directories to your ``PATH``, you can always run ``dffml`` command line
commands using Pythons module run syntax (``python -m``).

.. code-block:: console
    :test:

    $ python -m dffml version
    $ dffml version

You can now see the :doc:`/quickstart/model` to get started using DFFML!

Installing All Plugins
----------------------

If you want to install all of the machine learning model plugins that are
maintained as a part of the core repository, you can append ``[models]``.

.. tabs::

    .. group-tab:: Linux and MacOS

        .. code-block:: console

            $ python -m pip install -U dffml[models]

    .. group-tab:: Windows

        .. code-block:: console

            (.venv) C:\Users\username> python -m pip install -U dffml[models] -f https://download.pytorch.org/whl/torch_stable.html

If you want to install all of the machine learning model plugins and all the
data sources and DataFlow operations that are maintained as a part of the core
repository, you can append ``[all]``.

.. tabs::

    .. group-tab:: Linux and MacOS

        .. code-block:: console

            $ python -m pip install -U dffml[all]

    .. group-tab:: Windows

        .. code-block:: console

            (.venv) C:\Users\username> python -m pip install -U dffml[all] -f https://download.pytorch.org/whl/torch_stable.html

Master Branch
-------------

If you want to stay on the bleeding edge of bug fixes, etc. You can install from
the master branch.

.. tabs::

    .. group-tab:: Linux and MacOS

        .. code-block:: console
            :test:

            $ python -m pip install -U "https://github.com/intel/dffml/archive/master.zip#egg=dffml"

    .. group-tab:: Windows

        .. code-block:: console

            (.venv) C:\Users\username> python -m pip install -U "https://github.com/intel/dffml/archive/master.zip#egg=dffml"

You can also install the bleeding edge version of any plugin. To get the
subdirectory you should use, take the package name on PyPi and remove ``dffml-``
and replace ``-`` with ``/``.

.. tabs::

    .. group-tab:: Linux and MacOS

        .. code-block:: console
            :test:

            $ python -m pip install -U "https://github.com/intel/dffml/archive/master.zip#egg=dffml" \
                "https://github.com/intel/dffml/archive/master.zip#egg=dffml-feature-git&subdirectory=feature/git"

    .. group-tab:: Windows

        .. code-block:: console

            (.venv) C:\Users\username> python -m pip install -U "https://github.com/intel/dffml/archive/master.zip#egg=dffml" ^
                "https://github.com/intel/dffml/archive/master.zip#egg=dffml-feature-git&subdirectory=feature/git"

There's an online IDE based on Theia (similar to VS Code) called GitPod that
gives you a setup development environment to get started working with/on DFFML
right away. However, it comes with the master branch installed, you'll need to
run the above commands to get the latest released version.

.. image:: https://gitpod.io/button/open-in-gitpod.svg
   :target: https://gitpod.io/#https://github.com/intel/dffml

Ubuntu
------

For Ubuntu 20.XX python3 means Python 3.8 so far as ``apt`` is concerend.

.. code-block:: console

    $ sudo apt-get update && sudo apt-get install -y python3 python3-pip

For Ubuntu 18.XX python3 means Python 3.6 so far as ``apt`` is concerend.
However, ``python3-pip`` works for all 3.X versions. So you'll need to install
the following packages to get ``python3.7`` with ``pip``.

.. code-block:: console

    $ sudo apt-get update && sudo apt-get install -y python3.7 python3-pip

Docker
------

This is a good option if you don't want to deal with installing Python 3.7.

.. code-block:: console

    $ docker pull intelotc/dffml

You can also build the container image yourself if you'd like.

.. code-block:: console

    $ docker build -t intelotc/dffml .

You can then make a bash function to run the dffml docker container.

.. code-block:: bash

    dffml() {
      docker run --rm -ti \
        -v $HOME/.local:/home/$USER/.local/ \
        -v $HOME/.cache:/home/$USER/.cache/ \
        -v $PWD:/workdir -w /workdir \
        -e UID=$(id -u) -e USER=$USER \
        intelotc/dffml $@
    }

This creates an alias that takes your current working directory and mounts it
into ``/workdir`` as well as your ``$HOME/.local`` to the same in the container.

With the alias, you can run ``dffml`` commands as if you'd installed via
``pip``.

.. code-block:: console

    $ dffml list

Keep in mind that if you're working on files they can only be ones in your
current working directory, and if you want to access network resources and they
are on your host, you'll have to talk to ``172.17.0.1`` (docker0 inet address)
instead of ``localhost`` or ``127.0.0.1``.

The purpose of mounting ``$HOME/.local`` is so that if you want to
``pip install`` anything, you can, and it will persist between invocations due
to that being on the host.

If you wan to run ``pip`` you can put it after ``dffml``.

.. code-block:: console

    $ dffml pip install example
