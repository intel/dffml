"""
Machine Learning models implemented with `scikit-learn <https://scikit-learn.org/stable/>`_.
Models are saved under the directory in subdirectories named after the hash of
their feature names.

**General Usage:**

Training:

.. code-block:: console

    $ dffml train \\
        -model SCIKIT_MODEL_ENTRYPOINT \\
        -model-features FEATURE_DEFINITION \\
        -model-predict TO_PREDICT \\
        -model-SCIKIT_PARAMETER_NAME SCIKIT_PARAMETER_VALUE \\
        -sources f=TRAINING_DATA_SOURCE_TYPE \\
        -source-filename TRAINING_DATA_FILE_NAME \\
        -log debug

Testing and Accuracy:

.. code-block:: console

    $ dffml accuracy \\
        -model SCIKIT_MODEL_ENTRYPOINT \\
        -model-features FEATURE_DEFINITION \\
        -model-predict TO_PREDICT \\
        -sources f=TESTING_DATA_SOURCE_TYPE \\
        -source-filename TESTING_DATA_FILE_NAME \\
        -log debug

Predicting with trained model:

.. code-block:: console

    $ dffml predict all \\
        -model SCIKIT_MODEL_ENTRYPOINT \\
        -model-features FEATURE_DEFINITION \\
        -model-predict TO_PREDICT \\
        -sources f=PREDICT_DATA_SOURCE_TYPE \\
        -source-filename PREDICT_DATA_FILE_NAME \\
        -log debug


**Models Available:**

+----------------+-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Type           | Model                         | Entrypoint     | Parameters                                                                                                                                                                                    |
+================+===============================+================+===============================================================================================================================================================================================+
| Regression     | LinearRegression              | scikitlr       | `scikitlr <https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html#sklearn.linear_model.LinearRegression/>`_                                             |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | ElasticNet                    | scikiteln      | `scikiteln <https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.ElasticNet.html#sklearn.linear_model.ElasticNet/>`_                                                        |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | BayesianRidge                 | scikitbyr      | `scikitbyr <https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.BayesianRidge.html#sklearn.linear_model.BayesianRidge/>`_                                                  |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | Lasso                         | scikitlas      | `scikitlas <https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html#sklearn.linear_model.Lasso/>`_                                                                  |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | ARDRegression                 | scikitard      | `scikitard <https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.ARDRegression.html#sklearn.linear_model.ARDRegression/>`_                                                  |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | RANSACRegressor               | scikitrsc      | `scikitrsc <https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.RANSACRegressor.html#sklearn.linear_model.RANSACRegressor/>`_                                              |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | DecisionTreeRegressor         | scikitdtr      | `scikitdtr <https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeRegressor.html#sklearn.tree.DecisionTreeRegressor/>`_                                                  |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | GaussianProcessRegressor      | scikitgpr      | `scikitgpr <https://scikit-learn.org/stable/modules/generated/sklearn.gaussian_process.GaussianProcessRegressor.html#sklearn.gaussian_process.GaussianProcessRegressor/>`_                    |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | OrthogonalMatchingPursuit     | scikitomp      | `scikitomp <https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.OrthogonalMatchingPursuit.html#sklearn.linear_model.OrthogonalMatchingPursuit/>`_                          |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | Lars                          | scikitlars     | `scikitlars <https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lars.html#sklearn.linear_model.Lars/>`_                                                                   |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | Ridge                         | scikitridge    | `scikitridge <https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html#sklearn.linear_model.Ridge/>`_                                                                |
+----------------+-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Classification | KNeighborsClassifier          | scikitknn      | `scikitknn <https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.KNeighborsClassifier.html#sklearn.neighbors.KNeighborsClassifier/>`_                                          |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | AdaBoostClassifier            | scikitadaboost | `scikitadaboost <https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.AdaBoostClassifier.html#sklearn.ensemble.AdaBoostClassifier/>`_                                           |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | GaussianProcessClassifier     | scikitgpc      | `scikitgpc <https://scikit-learn.org/stable/modules/generated/sklearn.gaussian_process.GaussianProcessClassifier.html#sklearn.gaussian_process.GaussianProcessClassifier/>`_                  |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | DecisionTreeClassifier        | scikitdtc      | `scikitdtc <https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html#sklearn.tree.DecisionTreeClassifier/>`_                                                |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | RandomForestClassifier        | scikitrfc      | `scikitrfc <https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html#sklearn.ensemble.RandomForestClassifier/>`_                                        |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | QuadraticDiscriminantAnalysis | scikitqda      | `scikitqda <https://scikit-learn.org/stable/modules/generated/sklearn.discriminant_analysis.QuadraticDiscriminantAnalysis.html#sklearn.discriminant_analysis.QuadraticDiscriminantAnalysis/>`_|
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | MLPClassifier                 | scikitmlp      | `scikitmlp <https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPClassifier.html#sklearn.neural_network.MLPClassifier/>`_                                              |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | GaussianNB                    | scikitgnb      | `scikitgnb <https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.GaussianNB.html#sklearn.naive_bayes.GaussianNB/>`_                                                          |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | SVC                           | scikitsvc      | `scikitsvc <https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html#sklearn.svm.SVC/>`_                                                                                        |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | LogisticRegression            | scikitlor      | `scikitlor <https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html#sklearn.linear_model.LogisticRegression/>`_                                        |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | GradientBoostingClassifier    | scikitgbc      | `scikitgbc <https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.GradientBoostingClassifier.html#sklearn.ensemble.GradientBoostingClassifier/>`_                                |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | BernoulliNB                   | scikitbnb      | `scikitbnb <https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.BernoulliNB.html#sklearn.naive_bayes.BernoulliNB/>`_                                                        |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | ExtraTreesClassifier          | scikitetc      | `scikitetc <https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html#sklearn.ensemble.ExtraTreesClassifier/>`_                                            |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | BaggingClassifier             | scikitbgc      | `scikitbgc <https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.BaggingClassifier.html#sklearn.ensemble.BaggingClassifier/>`_                                                  |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | LinearDiscriminantAnalysis    | scikitlda      | `scikitlda <https://scikit-learn.org/stable/modules/generated/sklearn.discriminant_analysis.LinearDiscriminantAnalysis.html#sklearn.discriminant_analysis.LinearDiscriminantAnalysis/>`_      |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | MultinomialNB                 | scikitmnb      | `scikitmnb <https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.MultinomialNB.html#sklearn.naive_bayes.MultinomialNB/>`_                                                    |
+----------------+-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Clustering     | KMeans                        | scikitkmeans   | `scikitkmeans <https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html#sklearn.cluster.KMeans/>`_                                                                       |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | Birch                         | scikitbirch    | `scikitbirch <https://scikit-learn.org/stable/modules/generated/sklearn.cluster.Birch.html#sklearn.cluster.Birch/>`_                                                                          |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | MiniBatchKMeans               | scikitmbkmeans | `scikitmbkmeans <https://scikit-learn.org/stable/modules/generated/sklearn.cluster.MiniBatchKMeans.html#sklearn.cluster.MiniBatchKMeans/>`_                                                   |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | AffinityPropagation           | scikitap       | `scikitap <https://scikit-learn.org/stable/modules/generated/sklearn.cluster.AffinityPropagation.html#sklearn.cluster.AffinityPropagation/>`_                                                 |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | MeanShift                     | scikitms       | `scikitms <https://scikit-learn.org/stable/modules/generated/sklearn.cluster.MeanShift.html#sklearn.cluster.MeanShift/>`_                                                                     |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | SpectralClustering            | scikitsc       | `scikitsc <https://scikit-learn.org/stable/modules/generated/sklearn.cluster.SpectralClustering.html#sklearn.cluster.SpectralClustering/>`_                                                   |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | AgglomerativeClustering       | scikitac       | `scikitac <https://scikit-learn.org/stable/modules/generated/sklearn.cluster.AgglomerativeClustering.html#sklearn.cluster.AgglomerativeClustering/>`_                                         |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | OPTICS                        | scikitoptics   | `scikitoptics <https://scikit-learn.org/stable/modules/generated/sklearn.cluster.OPTICS.html#sklearn.cluster.OPTICS/>`_                                                                       |
+----------------+-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+


**Usage Example:**

Example below uses LinearRegression Model using the command line.

Let us take a simple example:

+----------------------+------------+--------------+--------+
| Years of Experience  |  Expertise | Trust Factor | Salary |
+======================+============+==============+========+
|          0           |     01     |      0.2     |   10   |
+----------------------+------------+--------------+--------+
|          1           |     03     |      0.4     |   20   |
+----------------------+------------+--------------+--------+
|          2           |     05     |      0.6     |   30   |
+----------------------+------------+--------------+--------+
|          3           |     07     |      0.8     |   40   |
+----------------------+------------+--------------+--------+
|          4           |     09     |      1.0     |   50   |
+----------------------+------------+--------------+--------+
|          5           |     11     |      1.2     |   60   |
+----------------------+------------+--------------+--------+

First we create the files

.. literalinclude:: /../model/scikit/examples/lr/train_data.sh

.. literalinclude:: /../model/scikit/examples/lr/test_data.sh

Train the model

.. literalinclude:: /../model/scikit/examples/lr/train.sh

Assess accuracy

.. literalinclude:: /../model/scikit/examples/lr/accuracy.sh

Output:

.. code-block::

    1.0

Make a prediction

.. literalinclude:: /../model/scikit/examples/lr/predict.sh

Output:

.. code-block:: json

    [
        {
            "extra": {},
            "features": {
                "Expertise": 13,
                "Trust": 0.7,
                "Years": 6
            },
            "key": "0",
            "last_updated": "2020-03-01T22:26:46Z",
            "prediction": {
                "Salary": {
                    "confidence": 1.0,
                    "value": 70.0
                }
            }
        }
    ]


Example usage of Linear Regression Model using python API:

.. literalinclude:: /../model/scikit/examples/lr/lr.py

Example below uses KMeans Clustering Model on a small randomly generated dataset.

.. code-block:: console

    $ cat > train.csv << EOF
   Col1,          Col2,        Col3,         Col4
   5.05776417,   8.55128116,   6.15193196,  -8.67349666
   3.48864265,  -7.25952218,  -4.89216256,   4.69308946
   -8.16207603,  5.16792984,  -2.66971993,   0.2401882
   6.09809669,   8.36434181,   6.70940915,  -7.91491768
   -9.39122566,  5.39133807,  -2.29760281,  -1.69672981
   0.48311336,   8.19998973,   7.78641979,   7.8843821
   2.22409135,  -7.73598586,  -4.02660224,   2.82101794
   2.8137247 ,   8.36064298,   7.66196849,   3.12704676
   EOF
    $ cat > test.csv << EOF
   Col1,             Col2,          Col3,         Col4,    cluster
   -10.16770144,   2.73057215,  -1.49351481,   2.43005691,    6
   3.59705381,  -4.76520663,  -3.34916068,   5.72391486,     1
   4.01612313,  -4.641852  ,  -4.77333308,   5.87551683,     0
   EOF
    $ dffml train \\
        -model scikitkmeans \\
        -model-features Col1:float:1 Col2:float:1 Col3:float:1 Col4:float:1 \\
        -sources f=csv \\
        -source-filename train.csv \\
        -source-readonly \\
        -log debug
    $ dffml accuracy \\
        -model scikitkmeans \\
        -model-features Col1:float:1 Col2:float:1 Col3:float:1 Col4:float:1\\
        -model-tcluster cluster:int:1 \\
        -sources f=csv \\
        -source-filename test.csv \\
        -source-readonly \\
        -log debug
    0.6365141682948129
    $ echo -e 'Col1,Col2,Col3,Col4\\n6.09809669,8.36434181,6.70940915,-7.91491768\\n' | \\
      dffml predict all \\
        -model scikitkmeans \\
        -model-features Col1:float:1 Col2:float:1 Col3:float:1 Col4:float:1 \\
        -sources f=csv \\
        -source-filename /dev/stdin \\
        -source-readonly \\
        -log debug
    [
        {
            "extra": {},
            "features": {
                "Col1": 6.09809669,
                "Col2": 8.36434181,
                "Col3": 6.70940915,
                "Col4": -7.91491768
            },
            "last_updated": "2020-01-12T22:51:15Z",
            "prediction": {
                "confidence": 0.6365141682948129,
                "value": 2
            },
            "key": "0"
        }
    ]

Example usage of KMeans Clustering Model using python API:

.. code-block:: python

    from dffml import CSVSource, Features, DefFeature
    from dffml.noasync import train, accuracy, predict
    from dffml_model_scikit import KMeansModel

    model = KMeansModel(
        features=Features(
            DefFeature("Col1", float, 1),
            DefFeature("Col2", float, 1),
            DefFeature("Col3", float, 1),
            DefFeature("Col4", float, 1),
        ),
        tcluster=DefFeature("cluster", int, 1)
    )

    # Train the model
    train(model, "train.csv")

    # Assess accuracy (alternate way of specifying data source)
    print("Accuracy:", accuracy(model, CSVSource(filename="test.csv")))

    # Make prediction
    for i, features, prediction in predict(
        model,
        {"Col1": 6.09809669, "Col2": 8.36434181, "Col3": 6.70940915, "Col4": -7.91491768},
    ):
        features["cluster"] = prediction["cluster"]["value"]
        print(features)

**NOTE**: `Transductive <https://scikit-learn.org/stable/glossary.html#term-transductive/>`_ Clusterers(scikitsc, scikitac, scikitoptics) cannot handle unseen data.
Ensure that `predict` and `accuracy` for these algorithms uses training data.

**Args**

- predict: Feature

  - Label or the value to be predicted
  - Only used by classification and regression models

- tcluster: Feature

  - True cluster, only used by clustering models
  - Passed with `accuracy` to return `mutual_info_score`
  - If not passed `accuracy` returns `silhouette_score`

- features: List of features

  - Features to train on

- directory: Path

  - default: ~/.cache/dffml/scikit-{entrypoint}
  - Directory where state should be saved

"""
from .scikit_models import *
