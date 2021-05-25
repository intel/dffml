3. Config Property Mutable vs Immutable
=======================================

Date: 2021-08-04

Status
------

Accepted

Context
-------

This document and 0004-Model-Saving-and-Loading were drafted at the same
time. See the 2021-05-25 Weekly Sync Meeting recording for more details.

Through discussion about model config properties in relation to modification of
hyperparameters we found that there are two kinds of config properties in
general (as it relates to this document).

- Immutable

    - Properties whose values are fundamentally tied to the object the config is
      used for. For the lifetime of the object.

    - If these config properties change, a new instance of the object using the
      config should be instantiated.

    - Think of these like the concious or the soul of the object. You cannot
      modify them, because then that would be a new object.

- Mutable

    - Properties whose values may could change over the lifetime of the
      object, yet the object is still fundamentally the same thing.

    - Think of these like the organs of the object. You could transplant an
      organ from one person into another, but you didn't change who that person
      is.

Decision
--------

Similar to the way :py:class:`typing.NamedTuple` works, config properties will
default to immutable. This way implementers of classes can assume they don't
need to deal with state changes to config properties unless they've explicitly
opted in.

We will require that a callback function be registered with the config class.
This way we ensure that modification of mutable values is handled somewhere.
To combat class authors from declaring properties as mutable, without
registering the callback. We'll raise an exception if the callback hasn't been
registered and any property is set or retrieved, or the instance is exported.

In the following example we have a hyperparameter, C. Out model wants to support
changes to it at runtime, so we mark it as mutable.

.. code-block:: python

    @config
    class MyModelConfig:
        C: int = field("C hyperparameter", mutable=True)

Since we've marked C as mutable, we must add a callback which deals with
mutations to the config object.

The callback we add accepts the key being modified within the config structure
and the value it was set to. For demonstration purposes we will use the value of
C in the model object. The callback's use of :py:func:`setattr` when the value
of C is updated in the config structure results in the value of C in the model
object also changing.

.. code-block:: python

    class MyModel(Model):
        CONFIG = MyModelConfig
        CONTEXT = ModelConfig

        def __init__(self, config):
            # Callback which will change self.C when self.config.C is changed
            self.config.add_mutable_callback(lambda key, value: setattr(self, key, value))
            # Use the value of C
            self.C = self.config.C

    model = MyModel(C=0)
    assert model.C == 0
    model.config.C = 42
    assert model.C == 42

If a user wants to modify an immutable property, they must create a new instance
of the object/config.

Consequences
------------

The :py:func:`field <dffml.base.field>` function will need to be modified to add
a ``mutable`` keyword argument.

We need to figure out how we'll support modifying sub-objects of configs. This
is something we'll consider for the future. For example PyTorch has optimizers
and loss functions which are objects which reside in the config of the main
PyTorchModelConfig.
