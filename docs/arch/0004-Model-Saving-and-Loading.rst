4. Model Saving and Loading
===========================

Date: 2021-05-25

Status
------

Draft

Context
-------

See :doc:`0003-Config-Property-Mutable-vs-Immutable` for more context. These
documents we started during the same Weekly Sync Meeting (2021-05-25).

We currently have inconsistencies in the models are saved and loaded. Due to
changes in the codebase over time with lax cleanup scrutiny.

We want to formalize how models are saved and loaded. How they interact with
their config structures, and which properties take precedence (saved or in
memory config properties).

We have following cases:

Model is instantiated with config. No existing saved state in directory.

.. code-block:: python

    model = ModelClass(
        directory="model_dir",
    )
    assert model.config.directory.is_dir() == False

Model is instantiated with config. Saved state in directory.

.. code-block:: python

    model = ModelClass(
        directory="model_dir",
    )
    assert model.config.directory.is_dir() == True

In our thoughts about implementing auto ML, we knew that there will be Model
config properties that are tunable, and some that are not tunable. For something
like auto ML which spans across models, we knew that we'd have to add a standard
way of defining tunable vs. non-tunable properties.

Within the context of the auto ML discussion, mutable vs. immutable becomes
tunable vs. non-tunable.

- Immutable: Architecture parameters which fundamentally alter the model, if
  these change it's not the same model.

- Mutable: Hyper parameters which we might want change.

Decision
--------

If a model config property is that mutable, and a saved value is present and
also a value in memory is present. The in memory value SHOULD override the saved
value.

.. todo::

  - Need to figure out default values.

    - Record that property should be default value?

    - What happens if package version changes?

      - Should we record what default value was and use old value in event of
        change? Or should we use the new value?

Consequences
------------

If the user wants to modify an immutable property, user must create a new
instance of the object/config since the property cannot be modified.

.. code-block:: python

    model = ModelClass(Z=0x5a)
    with unittest.TestCase().assertRaises(ConfigPropertyImmutable):
        model.config.Z = 0x00

If a model is instantiated with config and saved state exists within a
directory, saved state may conflict with instantiated model config properties.

In the following case, C is a mutable property. When we load the model, the in
memory value of ``1000000`` will take precedence over the saved state of ``42``.

.. code-block:: python

    model = ModelClass(
        directory="model_dir",
        C=1000000,
    )
    assert model.config.directory.is_dir() == True
    # Saved value of C is 42
    # Saved value of C will become 1000000 on load, due to override
