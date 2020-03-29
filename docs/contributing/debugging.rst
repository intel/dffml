Debugging
=========

The following are ways to debug issues you might run into when working on DFFML.

Many times issues are because a package you are working on is not installed in
development mode. First try checking ``~/.local/lib/python3.7/site-packages/`` and
if you see anything other than ``.egg-link`` behind the name of the ``dffml``
package you are working on, you probably need to delete that package and
re-install it in development mode (``pip install -e``).

Plugin Loading / Entrypoint Issues
----------------------------------

If you can't load the plugin you've been working on via the command line interface, HTTP API, etc. It's probably an entry point issue.

The ``dev`` service has a helper command to help you debug issues with installed
entrypoints.

.. code-block:: console

    $ dffml service dev entrypoints list dffml.model
    tfdnnc = dffml_model_tensorflow.dnnc:DNNClassifierModel -> dffml-model-tensorflow 0.2.0 (/home/user/Documents/python/dffml/model/tensorflow)
    scratchslr = dffml_model_scratch.slr:SLR -> dffml-model-scratch 0.0.1 (/home/user/Documents/python/dffml/model/scratch)
    scikitadaboost = dffml_model_scikit.scikit_models:AdaBoostClassifierModel -> dffml-model-scikit 0.0.1 (/home/user/Documents/python/dffml/model/scikit)
    scikitdtc = dffml_model_scikit.scikit_models:DecisionTreeClassifierModel -> dffml-model-scikit 0.0.1 (/home/user/Documents/python/dffml/model/scikit)
    scikitgnb = dffml_model_scikit.scikit_models:GaussianNBModel -> dffml-model-scikit 0.0.1 (/home/user/Documents/python/dffml/model/scikit)
    scikitgpc = dffml_model_scikit.scikit_models:GaussianProcessClassifierModel -> dffml-model-scikit 0.0.1 (/home/user/Documents/python/dffml/model/scikit)
    scikitknn = dffml_model_scikit.scikit_models:KNeighborsClassifierModel -> dffml-model-scikit 0.0.1 (/home/user/Documents/python/dffml/model/scikit)
    scikitlr = dffml_model_scikit.scikit_models:LinearRegressionModel -> dffml-model-scikit 0.0.1 (/home/user/Documents/python/dffml/model/scikit)
    scikitmlp = dffml_model_scikit.scikit_models:MLPClassifierModel -> dffml-model-scikit 0.0.1 (/home/user/Documents/python/dffml/model/scikit)
    scikitqda = dffml_model_scikit.scikit_models:QuadraticDiscriminantAnalysisModel -> dffml-model-scikit 0.0.1 (/home/user/Documents/python/dffml/model/scikit)
    scikitrfc = dffml_model_scikit.scikit_models:RandomForestClassifierModel -> dffml-model-scikit 0.0.1 (/home/user/Documents/python/dffml/model/scikit)
    scikitsvc = dffml_model_scikit.scikit_models:SVCModel -> dffml-model-scikit 0.0.1 (/home/user/Documents/python/dffml/model/scikit)

