.. _model_tutorial:

New Model Tutorial
==================

If you have some data and want to do machine learning on it, you probably want
to head over to the :ref:`plugin_models` plugins. This tutorial is for
implementing a machine learning algorithm. Which is probably what you want if
there's not an existing plugin for your algorithm.

DFFML is not like PyTorch or TensorFlow. It's higher level than those. However,
that doesn't mean it *has* to be higher level. You can use the lower level APIs
of any library, or no library if you wanted.

For this tutorial we'll be implementing our own machine learning algorithm from
scratch, which means that we're not using a machine learning focused library to
handle calculations for us.

.. warning::

    This tutorial needs updating. It will be updated to follow the way
    the `scratch model <https://github.com/intel/dffml/blob/master/model/scratch/dffml_model_scratch/slr.py>`_
    works. For now you might want to skim through this, and then look at that as
    a reference.

You'll most likely want to use a popular machine learning framework eventually
within your model class. For an example on how one might use ``scikit`` see the
code for the `scikit models <https://github.com/intel/dffml/blob/master/model/scikit/dffml_model_scikit/scikit_base.py>`_.

Create the Package
------------------

To create a new model we first create a new python package. DFFML has a script
to create it for you.

We're going to create a model that matches a new record exactly to anything it's
seen before. If it has seen it before it will be 100% confident. If it hasn't
seen it before it'll pick a random classification and assign that as it's
prediction with a 0% confidence.

.. code-block:: console

    $ dffml service dev create model my-model

This creates a Python package for you with a model that does nothing, called
``MiscModel``, and some useless tests.

Edit the model
--------------

Now we'll go through the three methods of a ``Model`` and fill them out.

Imports
~~~~~~~

We're going to need a few modules from the standard library, let's import them.

.. code-block:: python

    import json
    import random
    import hashlib

Class Name
~~~~~~~~~~

Let's once again rename ``Misc`` to ``Hindsight``, this time the class in the file.

.. code-block:: python

    class Hindsight(Model):
        '''
        A model which matches a new record exactly to anything it's seen before. If it
        has seen it before it will be 100% confident. If it hasn't seen it before
        it'll pick a random classification and assign that as it's prediction with a
        0% confidence.
        '''

        def __init__(self, model_dir: Optional[str] = None) -> None:
            super().__init__()
            # We aren't worring about saving and loading our model in this tutorial.
            # You should implement it when you write your model for real.
            self.model_dir = model_dir
            # Let's add a dict where we'll store what we know about previous records.
            self.mem = {}

Train
~~~~~

This model predicts completely based on what features has seen as they map to a
classification.

As such, we're going to take the JSON representation of each set of feature data
for each record we are given to train on, and hash it, storing the hash as the key
in our ``self.mem`` dict, and the value as the classification. This will let us
hash the feature data of future records we are asked to predict on and pull their
expected classification (for ones we've seen before).

.. code-block:: python

    async def train(self, sources: Sources):
        '''
        Train using records as the data to learn from.
        '''
        async for record in sources.with_features(features):
            # Make sure we are only dealing with classifications we care about
            if record.classification() in classifications:
                # Hash the data of the record and map it to the classification
                as_json = bytes(json.dumps(record.data.features))
                hash_json = hashlib.sha384(as_json).hexdigest()
                self.mem[hash_json] = record.classification()

Accuracy
~~~~~~~~

You could implement this by passing ``sources.classified_with_features(features)``
to predict and seeing how many it got right. However, we're going to skip that
in this tutorial (because we know the accuracy of this demo model will suck).

.. code-block:: python

    async def accuracy(self, sources: Sources) -> Accuracy:
        '''
        Evaluates the accuracy of our model after training using the input records
        as test data.
        '''
        # Lies
        return 1.0

Predict
~~~~~~~

The prediction, we'll just need to hash the features of each record we're asked to
make a prediction for. And see if it's in the existing mapping. If not, then
we'll just choose a random classification for it and call that good (with a 0%
confidence).

.. code-block:: python

    async def predict(self, records: AsyncIterator[Record]) -> \
                    AsyncIterator[Tuple[Record, Any, float]]:
        '''
        Uses trained data to make a prediction about the quality of a record.
        '''
        # Pull all records which have the features we are interested in.
        async for record in records:
            # Hash the data of the record and map it to the classification
            as_json = bytes(json.dumps(record.data.features()), 'utf-8')
            hash_json = hashlib.sha384(as_json).hexdigest()
            # If the mapping exists then that's what we'll predict
            if hash_json in self.mem:
                # Send it back with 100% (1.0) confidence
                yield record, self.mem[hash_json], 1.0
            else:
                # The feature hash doesn't exist in our mapping.
                # Pick a random classification and yield it with 0 confidence
                yield record, random.choice(self.parent.config.classifications), 0.0

Correct the plugin load path
----------------------------

Since we changed the name from ``misc`` to ``hindsight``, we have to change the path
in ``setup.py`` which will load our model.

.. code-block:: python

    entry_points={
        'dffml.model': [
            'hindsight = my_model.hindsight:Hindsight',
        ],
    },

Test the new model
------------------

Lets modify the test case to verify that we did this right.

Change the import path
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from my_model.hindsight import Hindsight

Change the class name
~~~~~~~~~~~~~~~~~~~~~

Change the test class's name, and make sure ``cls.model`` is instantiating a
``Hindsight`` model instead of the ``Misc`` model.

.. code-block:: python

    class TestHindsight(AsyncTestCase):

        @classmethod
        def setUpClass(cls):
            cls.model_dir = tempfile.TemporaryDirectory()
            # Make sure to change the line below this from Misc to Hindsight!!!
            cls.model = Hindsight()
            cls.model.model_dir = cls.model_dir.name
            cls.feature = StartsWithA()
            cls.features = Features(cls.feature)
            cls.classifications = ['a', 'not a']

Run the tests
~~~~~~~~~~~~~

.. code-block:: console

    $ python3.7 setup.py test
