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

Docker
------

This is a good option if you don't want to deal with installing Python 3.7.

.. code-block:: bash

    docker pull intelotc/dffml

.. code-block:: bash

    docker build -t dffml .

You can then make bash function to run the dffml docker container.

.. code-block:: bash

    dffml() {
      docker run --rm -ti \
        -v $HOME/.local:/home/$USER/.local/ \
        -v $HOME/.cache:/home/$USER/.cache/ \
        -v $PWD:/workdir -w /workdir -e UID=$(id -u) -e USER=$USER dffml $@
    }

This creates an alias that takes your current working directory and mounts it
into `/workdir` as well as your `$HOME/.local` to the same in the container.

With the alias, you can run `dffml` commands as you would if installed via
`pip`.

.. code-block:: bash

    dffml list

Keep in mind that if you're working on files they can only be ones in your
current working directory, and if you want to access network resources and they
are on your host, you'll have to talk to `172.17.0.1` (docker0 inet address)
instead of `localhost` or `127.0.0.1`.

The purpose of mounting `$HOME/.local` is so that if you want to
`pip install` anything, you can, and it will persist between invocations due
to that being on the host.

If you wan to run `pip` you can put it after `dffml`.

.. code-block:: bash

    dffml pip install example
