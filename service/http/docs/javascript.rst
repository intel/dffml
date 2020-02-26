JavaScript
==========

This is an example of how you can use the web API from javascript. Create the
following files.

We'll import the API from ``api.js``, and our code will go in ``index.js``.

**index.html**

.. literalinclude:: /../service/http/examples/javascript/index.html
    :language: html

**index.js**

.. literalinclude:: /../service/http/examples/javascript/index.js
    :language: javascript

Be aware that we're about to upload to the your current working directory
(wherever your shell is right now). You should have created the ``index.html``
and ``index.js`` in this directory.

.. code-block:: console

    $ dffml service http server -port 8080 -insecure -js -upload-dir . -static .

Go to http://localhost:8080/index.html and pop open the console to see what
happened, it should look like this.

.. code-block::

    Created api http://localhost:8080 Object { endpoint: "http://localhost:8080" }
    Created training_source Object { plugin_type: "source", context_cls: DFFMLHTTPAPISourceContext(args), api: {…}, plugin: null, label: null, config: {} }
    Uploaded my_training_dataset.csv
    Configured training_source Object { plugin_type: "source", context_cls: DFFMLHTTPAPISourceContext(args), api: {…}, plugin: "csv", label: "my_training_dataset", config: {…} }
    Created training_sctx Object { api: {…}, parent: {…}, label: "my_training_dataset_context" }
    Created test_source Object { plugin_type: "source", context_cls: DFFMLHTTPAPISourceContext(args), api: {…}, plugin: null, label: null, config: {} }
    Uploaded my_test_dataset.csv
    Configured test_source Object { plugin_type: "source", context_cls: DFFMLHTTPAPISourceContext(args), api: {…}, plugin: "csv", label: "my_test_dataset", config: {…} }
    Created test_sctx Object { api: {…}, parent: {…}, label: "my_test_dataset_context" }
    Training records Object(4) [ {…}, {…}, {…}, {…} ]
    Array of training records Array(4) [ {…}, {…}, {…}, {…} ]
    Created model Object { plugin_type: "model", context_cls: DFFMLHTTPAPIModelContext(args), api: {…}, plugin: null, label: null, config: {} }
    Configured model Object { plugin_type: "model", context_cls: DFFMLHTTPAPIModelContext(args), api: {…}, plugin: "scikitlr", label: "mymodel", config: {…} }
    Created model context Object { api: {…}, parent: {…}, label: "mymodel_context" }
    Trained model context Object { api: {…}, parent: {…}, label: "mymodel_context" }
    Model context accuracy undefined
    Model context predict Object { mish_the_smish: {…} }
    Success!
