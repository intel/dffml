Models
======

.. toctree::
    :glob:
    :maxdepth: 2
    :caption: Contents:

    base

Creating A New Model
--------------------

Create the Package

To create a new model we first create a new python package. DFFML has a script
to creat it for you.

We're going to create a model that matches a new repo exactly to anything it's
seen before. If it has seen it before it will be 100% confident. If it hasn't
seen it before it'll pick a random classification and assign that as it's
prediction with a 0% confidence.

.. code-block:: console

    export YOUR_MODEL_NAME=history
    dffml service dev create model "${YOUR_MODEL_NAME}"

> All lower case, only underscores allowed.

This creates a package in which multiple models could live. We start with just
one, ``Misc`` which is now located in
``/path/to/dffml/model/$YOUR_MODEL_NAME/model/misc.py``.

Name the first model
--------------------

This model operates only based on what it's seen. So let's just call it
``hindsight``.

.. code-block:: console

    mv model/$YOUR_MODEL_NAME/dffml_model_$YOUR_MODEL_NAME/model/misc.py \
      model/$YOUR_MODEL_NAME/dffml_model_$YOUR_MODEL_NAME/model/hindsight.py

Open the file for editing and continue.

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
        A model which matches a new repo exactly to anything it's seen before. If it
        has seen it before it will be 100% confident. If it hasn't seen it before
        it'll pick a random classification and assign that as it's prediction with a
        0% confidence.
        '''

        def __init__(self, model_dir: Optional[str] = None) -> None:
            super().__init__()
            # We aren't worring about saving and loading our model in this tutorial.
            # You should implement it when you write your model for real.
            self.model_dir = model_dir
            # Let's add a dict where we'll store what we know about previous repos.
            self.mem = {}
Train
~~~~~

This model predicts completely based on what features has seen as they map to a
classification.

As such, we're going to take the JSON representation of each set of feature data
for each repo we are given to train on, and hash it, storing the hash as the key
in our ``self.mem`` dict, and the value as the classification. This will let us
hash the feature data of future repos we are asked to predict on and pull their
expected classification (for ones we've seen before).

.. code-block:: python

    async def train(self, sources: Sources, features: Features,
            classifications: List[Any], steps: int, num_epochs: int):
        '''
        Train using repos as the data to learn from.
        '''
        # Pull all repos which have classifications, and the features we are
        # interested in.
        async for repo in sources.classified_with_features(features):
            # Make sure we are only dealing with classifications we care about
            if repo.classification() in classifications:
                # Hash the data of the repo and map it to the classification
                as_json = bytes(json.dumps(repo.data.features))
                hash_json = hashlib.sha384(as_json).hexdigest()
                self.mem[hash_json] = repo.classification()

Accuracy
~~~~~~~~

You could implement this by passing ``sources.classified_with_features(features)``
to predict and seeing how many it got right. However, we're going to skip that
in this tutorial (because we know the accuracy of this demo model will suck).

.. code-block:: python

    async def accuracy(self, sources: Sources, features: Features,
            classifications: List[Any]) -> Accuracy:
        '''
        Evaluates the accuracy of our model after training using the input repos
        as test data.
        '''
        # Lies
        return 1.0

Predict
~~~~~~~

The prediction, we'll just need to hash the features of each repo we're asked to
make a prediction for. And see if it's in the existing mapping. If not, then
we'll just choose a random classification for it and call that good (with a 0%
confidence).

.. code-block:: python

    async def predict(self, repos: AsyncIterator[Repo], features: Features,
            classifications: List[Any]) -> \
                    AsyncIterator[Tuple[Repo, Any, float]]:
        '''
        Uses trained data to make a prediction about the quality of a repo.
        '''
        # Pull all repos which have the features we are interested in.
        async for repo in repos:
            # Hash the data of the repo and map it to the classification
            as_json = bytes(json.dumps(repo.data.features), 'utf-8')
            hash_json = hashlib.sha384(as_json).hexdigest()
            # If the mapping exists then that's what we'll predict
            if hash_json in self.mem:
                # Send it back with 100% (1.0) confidence
                yield repo, self.mem[hash_json], 1.0
            else:
                # The feature hash doesn't exist in our mapping.
                # Pick a random classification and yield it with 0 confidence
                yield repo, random.choice(classifications), 0.0

Correct the plugin load path
----------------------------

Since we changed the name from ``misc`` to ``hindsight``, we have to change the path
in ``setup.py`` which will load our model.

.. code-block:: python

    entry_points={
        'dffml.model': [
            'hindsight = dffml_model_history.model.hindsight:Hindsight',
        ],
    },

Test the new model
------------------

Lets modify the test case to verify that we did this right.

Change the import path
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from dffml_model_history.model.hindsight import Hindsight

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

    cd model/$YOUR_MODEL_NAME
    python3.7 setup.py test
