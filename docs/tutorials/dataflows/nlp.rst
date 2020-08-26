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

    $ pip install -U dffml-model-tensorflow dffml-operations-nlp

Operation `remove_stopwords` cleans the text by removing most commanly used words which give the text little or no information eg. but, or, yet, it, is, am, etc.
These words are called `StopWords`. 
Operation `get_embedding` maps the tokens in the text to their corresponding word-vectors. Here we will use embeddings from `en_core_web_sm` spacy model.
You can use other models like `en_core_web_md`, `en_core_web_lg` for better results but these are bigger in size and may take a while to download.

Let's first download the `en_core_web_sm` model.

.. code-block:: console

    $ python -m spacy download en_core_web_sm

Create training data:

.. literalinclude:: /../examples/nlp/train_data.sh

Now we will create a dataflow to describe how the text feature (`sentence`) will be processed.

.. literalinclude:: /../examples/nlp/create_dataflow.sh

Operation `get_embedding` takes `pad_token` as input (here `<PAD>`) to append to sentences of length smaller
than `max_len` (here 10). A sentence which has length greater than `max_len` is truncated to have length equal to `max_len`.

To visualize the dataflow run:

.. literalinclude:: /../examples/nlp/dataflow_diagram.sh

Copy and pasting the output of the above code into the
`mermaidjs live editor <https://mermaidjs.github.io/mermaid-live-editor>`_
results in the graph.

.. image:: /.. /examples/nlp/dataflow_diagram.svg

We can now use this dataflow to preprocess the data and make it ready to be fed into model:

.. literalinclude:: /../examples/nlp/train.sh

As shown in the above command, a single input feature to model (here embedding) is of shape `(1, max_len, size_of_embedding)`.
Here we have taken `max_len` as 10 and the embedding size of `en_core_web_sm` is 96. So the resulting size of one input feature
is (1,10,96).

Assess accuracy:

.. literalinclude:: /../examples/nlp/accuracy.sh

The output is:

.. code-block:: console

    0.5

Create test data:

.. literalinclude:: /../examples/nlp/test_data.sh


Make prediction on test data:

.. literalinclude:: /../examples/nlp/predict.sh

The output is:

.. code-block:: console

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

Create training data:

.. literalinclude:: /../examples/nlp/train_data.sh

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

.. literalinclude:: /../examples/nlp/sklearn/create_dataflow.sh

To visualize the dataflow run:

.. literalinclude:: /../examples/nlp/sklearn/dataflow_diagram.sh

We can now use this dataflow to preprocess the data and make it ready to be fed into model:

.. literalinclude:: /../examples/nlp/sklearn/train.sh

Assess accuracy:

.. literalinclude:: /../examples/nlp/sklearn/accuracy.sh

The output is:

.. code-block:: console

    1.0

Create test data:

.. literalinclude:: /../examples/nlp/sklearn/test_data.sh

Make prediction on test data:

.. literalinclude:: /../examples/nlp/sklearn/predict.sh

The output is:

.. code-block:: console

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
