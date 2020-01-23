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

.. code-block:: python

    def double_ret(
        super_cool_arg, *, other_very_cool_arg: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, Tuple]:
        """
        This is the short description.

        This is the longer description.

        Parameters
        ----------
        table_name : str
            Name of the table.
        data : dict, optional
            Columns names are keys, values are data to insert.

        Returns
        -------
        str_super_cool_arg : str
            ``super_cool_arg`` as a string
        keys_and_values : tuple
            Keys and values of ``other_very_cool_arg`` returned as a tuple. Keys
            are at index 0, values are at index 1.

        Examples
        -------
        Here's how you use use this function

        >>> double_ret(42, other_very_cool_arg={"feed": 0xFACE})
        ("42", ("feed"], [0xFACE],))
        """
        return (
            str(super_cool_arg),
            tuple(other_very_cool_arg.keys(), other_very_cool_arg.values()),
        )

