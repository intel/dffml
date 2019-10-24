"""
.. note::

    It's important to keep the hidden layer config and feature config the same
    across invocations of train, predict, and accuracy methods.

    Models are saved under the ``directory`` parameter in subdirectories named
    after the hash of their feature names and hidden layer config. Which means
    if any of those parameters change between invocations, it's being told to
    look for a different saved model.
"""
