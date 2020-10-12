Flower17 Species Classification
===============================

This example will show you how to train and test a model on the `FLOWER17` dataset.
This dataset contains 17 classes of flower species, each having 80 images.

Download the dataset and verify with with ``sha384sum``.

.. literalinclude:: /../examples/flower17/dataset.sh

.. code-block:: console

    17flowers.tgz: OK

Extract the dataset.

.. code-block:: console

    $ tar -xzf 17flowers.tgz

All the images are now in a folder called `jpg`.
We split these images into flower_dataset/train and flower_dataset/test directories,
each directory containing sub-directories corresponding to the 17 flower classes using **split.py**.

**split.py**

.. literalinclude:: /../examples/flower17/split.py

We execute the split.py file. The train directory will contain 70 images for each class while
the test directory will contain 10 images for each class.

.. code-block:: console

    $ python split.py

Now that we have our flower dataset ready, we can perform classification of the flower species.
For this example, we will be going through 2 approaches:

.. toctree::
    :maxdepth: 2

    Using OpenCV to extract features and then training on a Scikit-Learn model<flower17_scikit>
    The Transfer Learning approach with Convolution Neural Networks<flower17_pytorch>
