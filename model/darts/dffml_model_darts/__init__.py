"""
Time series models implemented with `Darts <https://unit8co.github.io/darts/>`_.


**General Usage:**

Training:

.. code-block:: console

    $ dffml train \\
        -model DARTS_MODEL_ENTRYPOINT \\
        -model-features FEATURE_DEFINITION \\
        -model-predict TO_PREDICT \\
        -model-directory MODEL_DIRECTORY \\
        -model-DARTS_PARAMETER_NAME SCIKIT_PARAMETER_VALUE \\
        -sources f=TRAINING_DATA_SOURCE_TYPE \\
        -source-filename TRAINING_DATA_FILE_NAME \\
        -log debug

Testing and Accuracy:

.. code-block:: console

    $ dffml accuracy \\
        -model DARTS_MODEL_ENTRYPOINT \\
        -model-features FEATURE_DEFINITION \\
        -model-predict TO_PREDICT \\
        -model-directory MODEL_DIRECTORY \\
        -sources f=TESTING_DATA_SOURCE_TYPE \\
        -source-filename TESTING_DATA_FILE_NAME \\
        -log debug

Predicting with trained model:

.. code-block:: console

    $ dffml predict all \\
        -model DARTS_MODEL_ENTRYPOINT \\
        -model-features FEATURE_DEFINITION \\
        -model-predict TO_PREDICT \\
        -model-directory MODEL_DIRECTORY \\
        -sources f=PREDICT_DATA_SOURCE_TYPE \\
        -source-filename PREDICT_DATA_FILE_NAME \\
        -log debug


**Models Available:**

+----------------+-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Model                         | Entrypoint                      | Parameters                                                                                                                                                                                    |
+================+===============================+================+===============================================================================================================================================================================================+
| Exponential Smoothing         | dartsexponentialsmoothing       | `dartsexponentialsmoothing <https://unit8co.github.io/darts/generated_api/darts.models.exponential_smoothing.html`_                                                                           |
|----------------+-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+


"""
from .darts_models import *
