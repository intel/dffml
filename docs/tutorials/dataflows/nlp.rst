Using NLP Operations
====================

These example will show you how to use DFFML operations to clean text data and train Tensorflow DNNClassifier model and Scikit Learn
Naive Bayes Classifier model using DFFML cli.

Preprocessing data and training DNNClassifier model
---------------------------------------------------

DFFML offers several :ref:`plugin_models`. For this example
we will be using the tensorflow DNNClassifier model
(:ref:`plugin_model_dffml_model_tensorflow_tfdnnc`) which is in the ``dffml-model-tensorflow`` package.

We will use two operations :ref:`plugin_operation_dffml_operations_nlp_remove_stopwords` and :ref:`plugin_operation_dffml_operations_nlp_get_embedding`.
Internally, both of these operations use `spacy <https://spacy.io/usage/spacy-101>`_ functions.

To install DNNClassifier model and the above mentioned operations run:

.. code-block:: console
    :test:

    $ python -m pip install -U dffml-model-tensorflow dffml-operations-nlp

Operation `remove_stopwords` cleans the text by removing most commanly used words which give the text little or no information eg. but, or, yet, it, is, am, etc.
These words are called `StopWords`. 
Operation `get_embedding` maps the tokens in the text to their corresponding word-vectors. Here we will use embeddings from `en_core_web_sm` spacy model.
You can use other models like `en_core_web_md`, `en_core_web_lg` for better results but these are bigger in size and may take a while to download.

Let's first download the `en_core_web_sm` model.

.. code-block:: console
    :test:

    $ python -m spacy download en_core_web_sm

.. warning::

    Spacy and aiohttp don't play nice together. If you have aiohttp installed
    you're going to get weird messages about the version of the ``chardet``
    package (``pkg_resources.ContextualVersionConflict``). To avoid this, run
    the download command and include aiohttp in the list of packages to
    download, since ``spacy`` is passing through to ``pip`` here.

    .. code-block:: console
        :test:

        $ python -m spacy download en_core_web_sm aiohttp

Create training data:

**train_data.csv**

.. code-block::
    :test:
    :filepath: train_data.csv

    sentence,sentiment
    What a pleasant morning,1
    Those were bad days,0
    My puppy plays all day,1
    Cats are evil,0

Now we will create a dataflow to describe how the text feature (`sentence`) will be processed.

.. code-block:: console
    :test:

    $ dffml dataflow create get_single remove_stopwords get_embedding \
        -inputs \
          '["embedding"]'=get_single_spec \
          "en_core_web_sm"=spacy_model_name_def \
          "<PAD>"=pad_token_def 10=max_len_def \
        -flow \
          '[{"seed": ["sentence"]}]'=remove_stopwords.inputs.text \
          '[{"seed": ["spacy_model_name_def"]}]'=get_embedding.inputs.spacy_model \
          '[{"seed": ["pad_token_def"]}]'=get_embedding.inputs.pad_token \
          '[{"seed": ["max_len_def"]}]'=get_embedding.inputs.max_len \
          '[{"remove_stopwords": "result"}]'=get_embedding.inputs.text \
          '[{"remove_stopwords": "result"}]'=get_embedding.inputs.text | \
        tee nlp_ops_dataflow.json

Operation `get_embedding` takes `pad_token` as input (here `<PAD>`) to append to sentences of length smaller
than `max_len` (here 10). A sentence which has length greater than `max_len` is truncated to have length equal to `max_len`.

To visualize the dataflow run:

.. code-block:: console
    :test:

    $ dffml dataflow diagram -stage processing -- nlp_ops_dataflow.json

Copy and pasting the output of the above code into the
`mermaidjs live editor <https://mermaidjs.github.io/mermaid-live-editor>`_
results in the graph.

.. image:: /.. /examples/nlp/dataflow_diagram.svg

We can now use this dataflow to preprocess the data and make it ready to be fed into model:

.. code-block:: console
    :test:

    $ dffml train \
        -model tfdnnc \
        -model-batchsize 100 \
        -model-hidden 5 2 \
        -model-clstype int \
        -model-predict sentiment:int:1 \
        -model-classifications 0 1 \
        -model-location tempdir \
        -model-features embedding:float:[1,10,96] \
        -sources text=df \
        -source-text-dataflow nlp_ops_dataflow.json \
        -source-text-features sentence:str:1 \
        -source-text-source csv \
        -source-text-source-filename train_data.csv \
        -log debug

As shown in the above command, a single input feature to model (here embedding) is of shape `(1, max_len, size_of_embedding)`.
Here we have taken `max_len` as 10 and the embedding size of `en_core_web_sm` is 96. So the resulting size of one input feature
is (1,10,96).

Assess accuracy:

.. code-block:: console
    :test:

    $ dffml accuracy \
        -model tfdnnc \
        -model-batchsize 100 \
        -model-hidden 5 2 \
        -model-clstype int \
        -model-predict sentiment:int:1 \
        -model-classifications 0 1 \
        -model-location tempdir \
        -model-features embedding:float:[1,10,96] \
        -sources text=df \
        -source-text-dataflow nlp_ops_dataflow.json \
        -source-text-features sentence:str:1 \
        -source-text-source csv \
        -source-text-source-filename train_data.csv \
        -log debug
    0.5

Create test data:

**test_data.csv**

.. code-block::
    :test:
    :filepath: test_data.csv

    sentence
    Cats play a lot

Make prediction on test data:

.. code-block:: console
    :test:

    $ dffml predict all \
        -model tfdnnc \
        -model-batchsize 100 \
        -model-hidden 5 2 \
        -model-clstype int \
        -model-predict sentiment:int:1 \
        -model-classifications 0 1 \
        -model-location tempdir \
        -model-features embedding:float:[1,10,96] \
        -sources text=df \
        -source-text-dataflow nlp_ops_dataflow.json \
        -source-text-features sentence:str:1 \
        -source-text-source csv \
        -source-text-source-filename test_data.csv \
        -pretty

            Key:    0
                                                       Record Features
    +------------------------------------------------------------------------------------------------------------------------------+
    |            sentence           |                                       Cats play a lot                                        |
    +------------------------------------------------------------------------------------------------------------------------------+
    |           embedding           |                  (0.32292864, 4.358501, 3.2268033, 1.87990 ... (length:10)                   |
    +------------------------------------------------------------------------------------------------------------------------------+

                                                            Prediction
    +------------------------------------------------------------------------------------------------------------------------------+
    |                                                          sentiment                                                           |
    +------------------------------------------------------------------------------------------------------------------------------+
    |           Value:  1           |                               Confidence:   0.5122595429420471                               |
    +------------------------------------------------------------------------------------------------------------------------------+


Preprocessing data and training Naive Bayes Classifier model
------------------------------------------------------------

Now we will see how to use traditional ML algorithm like Naive Bayes Classifier available in ``dffml-model-scikit`` (:ref:`plugin_model_dffml_model_scikit`) for
classification.

Install the Naive Bayes Classifier by installing ``dffml-model-scikit``

.. code-block:: console
    :test:

    $ python -m pip install -U dffml-model-scikit

Create training data:

**train_data.csv**

.. code-block::
    :test:
    :overwrite:
    :filepath: train_data.csv

    sentence,sentiment
    What a pleasant morning,1
    Those were bad days,0
    My puppy plays all day,1
    Cats are evil,0

But before we feed the data to model we need to convert it to vectors of numeric values.
Here we will use ``tfidf_vectorizer`` operation (:ref:`plugin_operation_dffml_operations_nlp_tfidf_vectorizer`) which is a wrapper around
sklearn `TfidfVectorizer. <https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html>`_

The dataflow will be similar to the one used above but with a slight modification. We will add an extra operation
``collect_output`` (:ref:`plugin_operation_dffml_operations_nlp_collect_output`) which will collect all the records before
forwarding them to next operation. This is to ensure that `tfidf_vectorizer` receives a list of sentence rather than a single
sentence at a time. 
The matrix returned by `tfidf_vectorizer` will be passed to ``extract_array_from_matrix`` (:ref:`plugin_operation_dffml_operations_nlp_extract_array_from_matrix`)
which will return the array corresponding to each sentence.

So, Let's modify the dataflow to use our new operations.

.. TODO(#870) Need to implement length() method for all sources
   Then we can get rid of passing 4 as the source_length

.. code-block:: console
    :test:

    $ dffml dataflow create \
        -inputs \
          '["extract_array_from_matrix.outputs.result"]'=get_single_spec \
          4=source_length \
        -flow \
          '[{"seed": ["sentence"]}]'=remove_stopwords.inputs.text \
          '[{"seed": ["source_length"]}]'=collect_output.inputs.length \
          '[{"remove_stopwords": "result"}]'=collect_output.inputs.sentence \
          '[{"collect_output": "all"}]'=tfidf_vectorizer.inputs.text \
          '[{"remove_stopwords": "result"}]'=extract_array_from_matrix.inputs.single_text_example \
          '[{"collect_output": "all"}]'=extract_array_from_matrix.inputs.collected_text \
          '[{"tfidf_vectorizer": "result"}]'=extract_array_from_matrix.inputs.input_matrix \
        -- \
          get_single \
          remove_stopwords \
          collect_output \
          extract_array_from_matrix \
          tfidf_vectorizer | \
        tee nlp_ops_dataflow.json

To visualize the dataflow run:

.. code-block:: console
    :test:

    $ dffml dataflow diagram -stage processing -- nlp_ops_dataflow.json

We can now use this dataflow to preprocess the data and make it ready to be fed into model:

.. code-block:: console
    :test:

    $ dffml train \
        -model scikitgnb \
        -model-features extract_array_from_matrix.outputs.result:float:1 \
        -model-predict sentiment:int:1 \
        -model-location tempdir \
        -sources text=df \
        -source-text-dataflow nlp_ops_dataflow.json \
        -source-text-features sentence:str:1 \
        -source-text-source csv \
        -source-text-source-filename train_data.csv \
        -log debug

Assess accuracy:

.. code-block:: console
    :test:

    $ dffml accuracy \
        -model scikitgnb \
        -model-features extract_array_from_matrix.outputs.result:float:1 \
        -model-predict sentiment:int:1 \
        -model-location tempdir \
        -sources text=df \
        -source-text-dataflow nlp_ops_dataflow.json \
        -source-text-features sentence:str:1 \
        -source-text-source csv \
        -source-text-source-filename train_data.csv \
        -log debug
    1.0

Create test data:

**test_data.csv**

.. code-block::
    :test:
    :overwrite:
    :filepath: test_data.csv

    sentence
    Such a pleasant morning
    Those were good days
    My cat plays all day
    Dogs are evil


We're going to make predictions on test data, but first we'll use the ``merge``
command to pre-process the data. The ``merge`` command takes data from one
source and puts it in another. We can take records from the preprocessing source
and put them in the JSON source as an intermediary format.

.. note::

    Processing of sentences occurs concurrently, resulting in seemingly
    randomized output order.

.. code-block:: console
    :test:

    $ dffml merge text=df temp=json \
        -source-text-dataflow nlp_ops_dataflow.json \
        -source-text-features sentence:str:1 \
        -source-text-source csv \
        -source-text-source-filename test_data.csv \
        -source-temp-filename test_data_preprocessed.json \
        -source-temp-allowempty \
        -source-temp-readwrite \
        -log debug
    $ cat test_data_preprocessed.json | python -m json.tool

Now we can make prediction on test data:

.. code-block:: console
    :test:

    $ dffml predict all \
        -model scikitgnb \
        -model-features extract_array_from_matrix.outputs.result:float:1 \
        -model-predict sentiment:int:1 \
        -model-location tempdir \
        -sources temp=json \
        -source-temp-filename test_data_preprocessed.json \
        -pretty

            Key:	1
                                            Record Features
    +------------------------------------------------------------------------------------------------+
    |        sentence        |                          Those were good days                         |
    +------------------------------------------------------------------------------------------------+
    |extract_array_from_matri|             0.0, 0.0, 0.7071067811865476, 0 ... (length:9)            |
    +------------------------------------------------------------------------------------------------+

                                            Prediction
    +------------------------------------------------------------------------------------------------+
    |                                           sentiment                                            |
    +------------------------------------------------------------------------------------------------+
    |       Value:  1        |                           Confidence:   1.0                           |
    +------------------------------------------------------------------------------------------------+

        Key:	2
                                            Record Features
    +------------------------------------------------------------------------------------------------+
    |        sentence        |                          My cat plays all day                         |
    +------------------------------------------------------------------------------------------------+
    |extract_array_from_matri|             0.5773502691896257, 0.577350269 ... (length:9)            |
    +------------------------------------------------------------------------------------------------+

                                            Prediction
    +------------------------------------------------------------------------------------------------+
    |                                           sentiment                                            |
    +------------------------------------------------------------------------------------------------+
    |       Value:  0        |                           Confidence:   1.0                           |
    +------------------------------------------------------------------------------------------------+

        Key:	0
                                            Record Features
    +------------------------------------------------------------------------------------------------+
    |        sentence        |                        Such a pleasant morning                        |
    +------------------------------------------------------------------------------------------------+
    |extract_array_from_matri|             0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0 ... (length:9)            |
    +------------------------------------------------------------------------------------------------+

                                            Prediction
    +------------------------------------------------------------------------------------------------+
    |                                           sentiment                                            |
    +------------------------------------------------------------------------------------------------+
    |       Value:  1        |                           Confidence:   1.0                           |
    +------------------------------------------------------------------------------------------------+

        Key:	3
                                            Record Features
    +------------------------------------------------------------------------------------------------+
    |        sentence        |                             Dogs are evil                             |
    +------------------------------------------------------------------------------------------------+
    |extract_array_from_matri|             0.0, 0.0, 0.0, 0.70710678118654 ... (length:9)            |
    +------------------------------------------------------------------------------------------------+

                                            Prediction
    +------------------------------------------------------------------------------------------------+
    |                                           sentiment                                            |
    +------------------------------------------------------------------------------------------------+
    |       Value:  0        |                           Confidence:   1.0                           |
    +------------------------------------------------------------------------------------------------+
