Data Cleanup Operations
=======================

In this example we are going to perform cleanup
operations on a real-world dataset.

In this example we will perform the following steps

- Writing cleanup operations dataflow
- Using merge command to see the preprocessed data
- Training our model on the preprocessed data
- Getting the accuracy of the model
- Checking the accuracy of the model without cleanup
  of the data

First install the data cleanup operations and scikit models

.. code-block:: console
    :test:

    $ python -m pip install dffml-operations-data dffml-model-scikit

Dataset
-------

The dataset we will be using is available on
kaggle https://www.kaggle.com/harlfoxem/housesalesprediction

you may go ahead and download the dataset

.. code-block:: console
    :test:

    $ curl -fLO https://github.com/intel/dffml/files/7046671/kc_house_data.csv

Data Cleanup Operations
-----------------------

We will be performing two cleanup operations on our dataset
- `standard_scaler` will normalize the dataset having
unit variance and standard deviation of 0
- `principal_component_analysis` will convert the data
into (number of samples, number of components)

.. code-block:: console
    :test:

    $ dffml dataflow create \
        -config \
            "kc_house_data.csv"=convert_records_to_list.source.config.filename \
            csv=convert_records_to_list.source.plugin \
        -inputs \
            '["records"]'=get_single_spec \
            '["bedrooms", "bathrooms", "sqft_living", "sqft_lot", "floors", "waterfront", "view", "condition", "grade", "sqft_above", "sqft_basement", "yr_built", "yr_renovated", "zipcode", "lat", "long", "sqft_living15", "sqft_lot15"]'=features \
            '["price"]'=predict_features \
            None=n_components \
        -flow \
            '[{"convert_records_to_list": "matrix"}]'=standard_scaler.inputs.data \
            '[{"standard_scaler": "result"}]'=principal_component_analysis.inputs.data \
            '[{"seed": ["n_components"]}]'=principal_component_analysis.inputs.n_components \
            '[{"principal_component_analysis": "result"}]'=convert_list_to_records.inputs.matrix \
            '[{"convert_records_to_list": "keys"}]'=convert_list_to_records.inputs.keys \
            --\
                convert_list_to_records \
                convert_records_to_list \
                principal_component_analysis \
                standard_scaler \
                get_single | \
        tee clean_ops.json

Merge Command
-------------

Now we will run the dataflow on our dataset, with
the help of merge command we can see what our preprocessed
data looks like.

.. code-block:: console
    :test:

    $ dffml merge text=df temp=csv \
        -source-text-dataflow clean_ops.json \
        -source-text-features price:float:1 bedrooms:float:1 bathrooms:float:1 sqft_living:float:1 sqft_lot:float:1 floors:str:1 waterfront:float:1 view:float:1 condition:float:1 grade:float:1 sqft_above:float:1 sqft_basement:float:1 yr_built:float:1 yr_renovated:float:1 zipcode:str:1 lat:float:1 long:float:1 sqft_living15:float:1 sqft_lot15:float:1 \
        -source-text-source csv \
        -source-text-source-filename kc_house_data.csv \
        -source-temp-filename preprocessed.csv \
        -source-temp-allowempty \
        -source-temp-readwrite \
        -log debug

    $ cat preprocessed.csv

Training
--------

Now we will train our model on the preprocessed
dataset that we just got using the merge command.

.. code-block:: console
    :test:

    $ dffml train \
        -model scikiteln \
        -model-features bedrooms:float:1 bathrooms:float:1 sqft_living:float:1 sqft_lot:float:1 floors:str:1 waterfront:float:1 view:float:1 condition:float:1 grade:float:1 sqft_above:float:1 sqft_basement:float:1 yr_built:float:1 yr_renovated:float:1 zipcode:str:1 lat:float:1 long:float:1 sqft_living15:float:1 sqft_lot15:float:1 \
        -model-predict price:float:1 \
        -model-location tempdir \
        -sources f=csv \
        -source-filename preprocessed.csv \
        -log debug

Accuracy
--------

After training of the dataset we can check the
accuracy of the model.

.. code-block:: console
    :test:

    $ dffml accuracy \
        -model scikiteln \
        -scorer exvscore \
        -features price:float:1 \
        -model-features bedrooms:float:1 bathrooms:float:1 sqft_living:float:1 sqft_lot:float:1 floors:str:1 waterfront:float:1 view:float:1 condition:float:1 grade:float:1 sqft_above:float:1 sqft_basement:float:1 yr_built:float:1 yr_renovated:float:1 zipcode:str:1 lat:float:1 long:float:1 sqft_living15:float:1 sqft_lot15:float:1 \
        -model-predict price:float:1 \
        -model-location tempdir \
        -sources f=csv \
        -source-filename preprocessed.csv \
        -log debug

Without Cleanup Operations
--------------------------

Here we will be checking what is the accuracy
of the model without performing cleanup operations.

.. code-block:: console
    :test:

    $ dffml train \
        -model scikiteln \
        -model-features bedrooms:float:1 bathrooms:float:1 sqft_living:float:1 sqft_lot:float:1 floors:str:1 waterfront:float:1 view:float:1 condition:float:1 grade:float:1 sqft_above:float:1 sqft_basement:float:1 yr_built:float:1 yr_renovated:float:1 zipcode:str:1 lat:float:1 long:float:1 sqft_living15:float:1 sqft_lot15:float:1 \
        -model-predict price:float:1 \
        -model-location tempdir \
        -sources f=csv \
        -source-filename kc_house_data.csv \
        -log debug

.. code-block:: console
    :test:

    $ dffml accuracy \
        -model scikiteln \
        -scorer exvscore \
        -features price:float:1 \
        -model-features bedrooms:float:1 bathrooms:float:1 sqft_living:float:1 sqft_lot:float:1 floors:str:1 waterfront:float:1 view:float:1 condition:float:1 grade:float:1 sqft_above:float:1 sqft_basement:float:1 yr_built:float:1 yr_renovated:float:1 zipcode:str:1 lat:float:1 long:float:1 sqft_living15:float:1 sqft_lot15:float:1 \
        -model-predict price:float:1 \
        -model-location tempdir \
        -sources f=csv \
        -source-filename kc_house_data.csv \
        -log debug

Conclusion
----------

We can see that after performing cleanup operations
and doing preprocessing on the data we have increased
our accuracy and also reduced our training time for the
models.
