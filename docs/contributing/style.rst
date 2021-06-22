Style
=====

This document talks about code formatting, conventions, documentation, and any
stylistic choices that we adhere to.

Try to run the formatters before every commit. This way, if you push up files
for review, they are easy to read, even if your pull request isn't yet ready to
merge.

Python File Formatting
----------------------

To install black in the environment

.. code-block:: console

    $ pip install black==19.10b0

Run the `black <https://github.com/psf/black>`_ formatter on all Python files.

.. code-block:: console

    $ black .

In VSCode open command pallete by Ctrl+Shift+p, open Settings(JSON) and add the properties.

.. code-block:: json

    {
        "editor.formatOnSave": true,
        "python.formatting.provider": "black",
    }

JavaScript File Formatting
--------------------------

Run the `js-beautify <https://github.com/beautify-web/js-beautify>`_ formatter
on all JavaScript files. Use the following options.

.. code-block:: console

    $ js-beautify -r -n -s 2 file_to_format.js

Naming Conventions
------------------

- Variables should always use underscores, as well as functions and methods.
- Classes should use CamelCase.

Imports
-------

Here's an example of how we style our imports.

.. code-block:: python

    import re
    import json
    import inspect
    import unittest.mock
    from typing import Dict, Any

    import sklearn.datasets

    from dffml.record import Record
    from dffml.configloader.configloader import BaseConfigLoader
    from dffml.util.asynctestcase import AsyncTestCase

    import dffml_model_scikit

    from .helpers import my_helper_func

Here's the generic format.

- Standard Library Packages

  - Imports from ``typing`` should always be last regardless of XMAS tree style.

- `Empty line`

- Third Party Packages

    - Anything that doesn't come with Python, things you ``pip install``.

- `Empty line`

- Any imports from DFFML (the main package)

- `Empty line`

- Any imports from DFFML plugins (dffml-plugin_type-name packages)

- `Empty line`

- Imports of other files from the package we're currently in (if we're this far
  nested, likely this might only happen in an example package like ``shouldi``
  or in the tests for an *Official* plugin).

In every block of imports (a block is a group of lines between empty lines), you
should be following reverse `reverse christmas tree
<https://lwn.net/Articles/758915/>`_ style. This means that lines with the least
characters go before lines with more characters. If you're feeling wordy you can
refer to this as "XMAS tree" instead of "reverse reverse christmas tree".

Docstrings
----------

We use Numpy style docstrings, as opposed to Google or the Sphinx default.

This is because Google does not support multiple return values, and it looks a
bit more organized to have multi line descriptions for arguments indented on the
following line.

More information on the Numpy docstiring format can be found
`here <https://numpydoc.readthedocs.io/en/latest/format.html>`_.

Example Docstring
+++++++++++++++++

.. literalinclude:: /../tests/util/double_ret.py
