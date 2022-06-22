Double Context Entry
====================

Double context entry is a pattern you will see throughout DFFML. It's used
almost everywhere for consistencies sake.

.. note::

   This was covered in the 2021-02-016 Weekly Sync meeting:
   https://youtu.be/OY_OfqB7rkY?t=657 (until 19:12).

DFFML uses ``asyncio`` heavily, as such when we talk about entering or exiting
contexts, we are always talking about the ``async`` context unless explicitly
stated.

Rules of the double context entry pattern
-----------------------------------------

- All objects are comprised of two classes

  - The parent

    - Usually responsible for saving / loading files, creating initial
      connections to databases.

  - The context (Which always have the suffix, "Context")

    - Usually responsible for transactions within a database, locks on
      sub resources, etc.

    - The methods of an object should reside in it's context.

Benefits of using this pattern
------------------------------

Many network attached resources will fall into this pattern. By applying it
uniformly, we make it so all classes have a future proof place to load network
resources when / if needed.

Example - Model
---------------

You can also keep model or sources loaded by passing in their contexts.
The advantage of this method is that we as the caller can control when
models are saved and loaded, and when sources are opened / closed (for
example if they are backed by a file).

**model.py**

.. literalinclude:: /../examples/tutorials/doublecontextentry/model.py
    :test:

.. code-block:: console
    :test:

    $ python model.py
    {'Years': 6, 'Salary': 70}
    {'Years': 7, 'Salary': 80}
