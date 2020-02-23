Style
=====

This document talks about code formatting, conventions, documentation, and any
stylistic choices that we adhere to.

File Formatting
---------------

We run the `black <https://github.com/psf/black>`_ formatter on all files. Try
to run it before every commit. This way, if you push up files for review, they
are easy to read, even if your pull request isn't yet ready to merge.

.. code-block:: console

    $ black .

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
    from dffml.config.config import BaseConfigLoader
    from dffml.util.asynctestcase import AsyncTestCase, IntegrationCLITestCase

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
  or in the tests for a *Core* plugin).

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

Mre information on the Numpy docstiring format can be found
`here <https://numpydoc.readthedocs.io/en/latest/format.html>`_.

Example Docstring
+++++++++++++++++

.. literalinclude:: /../tests/util/double_ret.py
