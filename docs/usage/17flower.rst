17flower dataset classification using Scikit-Learn
==================================================

This example will show you how to train and test a model on the `FLOWER17` dataset.
This dataset contains 17 classes of flower species, each having 80 images.

Download the dataset and verify with with ``sha256sum``.

.. literalinclude:: /../examples/flower17/dataset.sh

.. code-block:: console

    17flowers.tgz: OK

The model we'll be using is the `RandomForestClassifier` which is a part of 
``dffml-model-scikit``, a DFFML plugin which allows you to use Scikit-Learn via DFFML.
We'll also be using the various operations from ``dffml-operations-image``, which is
a DFFML plugin which allows you to do image processing via DFFML.
We can install them with ``pip``.

.. code-block:: console

    $ pip install -U dffml-model-scikit dffml-operations-image

Extract the dataset.

.. code-block:: console

    $ tar -xzf ~/Downloads/17flowers.tgz

All the images are now in a folder called `jpg`.
Let's split these images into flower_dataset/train and flower_dataset/test directories,
each directory containing sub-directories corresponding to the 17 flower classes.

.. literalinclude:: /../examples/flower17/split.py

.. code-block:: console

    $ python split.py

The train directory contains 65 images for each class while the test directory contains
15 images for each class.

Create a dataflow config file which will be used by the
:py:class:`DataFlowSource <dffml.source.df.DataFlowSource>` to preprocess
the data before feeding it to the model.

.. literalinclude:: /../examples/flower17/create_dataflow.sh

To visualize the dataflow run:

.. literalinclude:: /../examples/flower17/dataflow_diagram.sh

Copy and pasting the output of the above code into the
`mermaidjs live editor <https://mermaidjs.github.io/mermaid-live-editor>`
results in the graph.

.. image:: /.. /examples/flower17/dataflow_diagram.svg

Train the model.

.. literalinclude:: /../examples/flower17/train.sh

Assess the model's accuracy.

.. literalinclude:: /../examples/flower17/accuracy.sh

The output is:

.. code-block:: console

    0.27450980392156865

Create an ``unknown_images.csv`` file which contains the names of the images to predict on.

.. literalinclude:: /../examples/flower17/unknown_data.sh

Predict with the trained model.

.. literalinclude:: /../examples/flower17/predict.sh

Output

.. literalinclude:: /../examples/flower17/output.json
