Notes on Various Subsystems
===========================

DFFML is comprised of various subsystems. The following are some notes
that might be helpful when working on each of them.

Working on ``skel/``
--------------------

The packages in ``skel/`` are used to create new DFFML packages.

For example, to create a new package containing operations we run the following.

.. code-block:: console

    $ dffml service dev create operations dffml-operations-feedface

If you want to work on any of the packages in ``skel/``, you'll need to run the
``skel link`` command first fromt he ``dev`` service. This will symlink required
files in from ``common/`` so that testing will work.

.. code-block:: console

    $ dffml service dev skel link

