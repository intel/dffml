Codebase Layout
===============

.. contents:: :local:

Source Code
-----------

``REPLACE_IMPORT_PACKAGE_NAME/`` contains the codebase of the project. The
``tests/`` directory contains the unit and integration tests.

Documentation
-------------

- ``docs/`` contains the project documentation.

  - ``contributing/`` contains information on contributing to the project.

Python Packaging
----------------

.. contents:: :local:

MANIFEST.in
~~~~~~~~~~~

Files listed here are included in the archive of your package which is released.
If there is a file in your codebase and it's not listed here and it's not a
Python file it will not be in the released package.

``recursive-include`` with ``*`` at the end says to include everything under a
given directory.

.. literalinclude:: /../MANIFEST.in

entry_points.txt
~~~~~~~~~~~~~~~~

See Python's `Creating and discovering plugins
<https://packaging.python.org/guides/creating-and-discovering-plugins/>`_
documentation for how entry points are used to export plugins as well as
setuptool's `Entry Points
https://setuptools.pypa.io/en/latest/userguide/entry_point.html>_`
documentation.

.. literalinclude:: /../entry_points.txt

LICENSE
~~~~~~~

Your project's `LICENSE <https://opensource.org/licenses/alphabetical>`_

.. literalinclude:: /../LICENSE

README.rst
~~~~~~~~~~

This file is included in the archive of your package which is released. It is
also displayed on PyPi if you upload your package to PyPi.

setup.py
~~~~~~~~

This file is only around due to changes in the Python Packaging ecosystem.
Eventually it will no longer be required. It exists to point to the
``setup.cfg`` file until that file alone will suffice.

.. literalinclude:: /../setup.py

pyproject.toml
~~~~~~~~~~~~~~

This file is defined and it's format is outlined or referenced in:

- `PEP-518 <https://www.python.org/dev/peps/pep-0518/>`_

- `setuptools Dependency Management <https://setuptools.pypa.io/en/latest/userguide/dependency_management.html>_`

- `PEP-517 <https://www.python.org/dev/peps/pep-0517/>`_

- `PEP-440 <https://www.python.org/dev/peps/pep-0440/>`_

This file and ``setup.cfg`` define your package and it's build and run time
dependencies.

.. literalinclude:: /../pyproject.toml

setup.cfg
~~~~~~~~~

This file and ``pyproject.toml`` define your package and it's run time
dependencies.

- `setuptools quickstart <https://setuptools.pypa.io/en/latest/userguide/quickstart.html>_`

.. literalinclude:: /../setup.cfg
