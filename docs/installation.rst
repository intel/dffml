Installation
============

DFFML currently **only supports Python 3.7**. If your distribution's package
manager doesn't provide Python 3.7,
`pyenv <https://github.com/pyenv/pyenv#simple-python-version-management-pyenv>`_
is another good way to install it. You could also use the docker container.

DFFML is available via pip.

.. code-block:: console

    $ python3.7 -m pip install -U dffml

If you want to stay on the bleeding edge of bug fixes, etc. Install via git.

.. code-block:: console

    $ python3.7 -m pip install -U git+https://github.com/intel/dffml

If you want to install all of the machine learning model plugins that are
maintained as a part of the core repository, you can append ``[models]``.

.. code-block:: console

    $ python3.7 -m pip install -U dffml[models]

There's an online IDE based on Theia (similar to VS Code) called GitPod that
gives you a setup development environment to get started working with/on DFFML
right away. However, it comes with the master branch installed, you'll need to
run the above commands to get the lastest released version.

.. image:: https://gitpod.io/button/open-in-gitpod.svg
   :target: https://gitpod.io/#https://github.com/intel/dffml

Ubuntu
------

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
