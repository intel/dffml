Data Cleanup Operations
=======================

In this example we are going to perform cleanup
operations on a real-world dataset.

In this example we will perform the following steps

- Writing cleanup operations dataflow
- Using merge command to see the preprocessed data
- Training our model on the preprocessed data
- Getting the accuracy of the model

First install the data cleanup operations and scikit models

.. code-block:: console
    :test:

    $ python -m pip install dffml-operations-data dffml-model-scikit

Dataset
-------

The dataset we will be using is available on
kaggle https://www.kaggle.com/uciml/mushroom-classification

you may go ahead and download the dataset

.. code-block:: console
    :test:

    $ curl -fLO https://github.com/intel/dffml/files/7040983/mushrooms.csv

Data Cleanup Operations
-----------------------

We will be performing two cleanup operations on our dataset
- `ordinal_encoder` , As seen in the dataset all
the values are categorical values haivng a similar
relationship. So we can convert these categorical
values into numerical values.

Data Cleanup
------------

** cleanup_ops.sh **

.. code-block:: console
    :test:

    $ dffml dataflow create \
        -config \
            "mushrooms.csv"=convert_records_to_list.source.config.filename \
            csv=convert_records_to_list.source.plugin \
        -inputs \
            '["records"]'=get_single_spec \
            '["class","cap-shape","cap-surface","cap-color","bruises","odor","gill-attachment","gill-spacing","gill-size","gill-color","stalk-shape","stalk-root","stalk-surface-above-ring","stalk-surface-below-ring","stalk-color-above-ring","stalk-color-below-ring","veil-type","veil-color","ring-number","ring-type","spore-print-color","population","habitat"]'=features \
            '[]'=predict_features \
        -flow \
            '[{"convert_records_to_list": "matrix"}]'=ordinal_encoder.inputs.data \
            '[{"ordinal_encoder": "result"}]'=convert_list_to_records.inputs.matrix \
            '[{"convert_records_to_list": "keys"}]'=convert_list_to_records.inputs.keys \
            --\
                convert_list_to_records \
                convert_records_to_list \
                ordinal_encoder \
                get_single | \
        tee clean_ops.json

Data Merge
----------

To have a look at the preprocessed data, we can use 
the merge command.

** merge.sh **

.. code-block:: console
    :test:

    $ dffml merge text=df temp=csv \
        -source-text-dataflow clean_ops.json \
        -source-text-features class:float:1 cap-shape:float:1 cap-surface:float:1 cap-color:float:1 bruises:float:1 odor:float:1 gill-attachment:float:1 gill-spacing:float:1 gill-size:float:1 gill-color:float:1 stalk-shape:float:1 stalk-root:float:1 stalk-surface-above-ring:float:1 stalk-surface-below-ring:float:1 stalk-color-above-ring:float:1 stalk-color-below-ring:float:1 veil-type:float:1 veil-color:float:1 ring-number:float:1 ring-type:float:1 spore-print-color:float:1 population:float:1 habitat:float:1 \
        -source-text-source csv \
        -source-text-source-filename mushrooms.csv \
        -source-temp-filename preprocessed.csv \
        -source-temp-allowempty \
        -source-temp-readwrite \
        -log debug
    
    $ cat preprocessed.csv

Training
--------

Now we will be training our model using the preprocessed
dataset

** train.sh **

.. code-block:: console
    :test:

    $ dffml train \
        -model scikitmnb \
        -model-features cap-shape:float:1 cap-surface:float:1 cap-color:float:1 bruises:float:1 odor:float:1 gill-attachment:float:1 gill-spacing:float:1 gill-size:float:1 gill-color:float:1 stalk-shape:float:1 stalk-root:float:1 stalk-surface-above-ring:float:1 stalk-surface-below-ring:float:1 stalk-color-above-ring:float:1 stalk-color-below-ring:float:1 veil-type:float:1 veil-color:float:1 ring-number:float:1 ring-type:float:1 spore-print-color:float:1 population:float:1 habitat:float:1 \
        -model-predict class:str:1 \
        -model-location tempdir \
        -sources f=csv \
        -source-filename preprocessed.csv \
        -log debug

Accuracy
--------

After training the model we can now look for accuracy
of the trained model

** accuracy.sh **

.. code-block:: console
    :test:

    $ dffml accuracy \
        -model scikitmnb \
        -scorer logloss \
        -features class:str:1 \
        -model-features cap-shape:float:1 cap-surface:float:1 cap-color:float:1 bruises:float:1 odor:float:1 gill-attachment:float:1 gill-spacing:float:1 gill-size:float:1 gill-color:float:1 stalk-shape:float:1 stalk-root:float:1 stalk-surface-above-ring:float:1 stalk-surface-below-ring:float:1 stalk-color-above-ring:float:1 stalk-color-below-ring:float:1 veil-type:float:1 veil-color:float:1 ring-number:float:1 ring-type:float:1 spore-print-color:float:1 population:float:1 habitat:float:1 \
        -model-predict class:str:1 \
        -model-location tempdir \
        -sources f=csv \
        -source-filename preprocessed.csv \
        -log debug

Conclusion
----------

Thus, we performed cleanup operations on a classfication
dataset.
