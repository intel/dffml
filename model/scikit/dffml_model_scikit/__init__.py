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
        -model-location MODEL_DIRECTORY \\
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
        -model-location MODEL_DIRECTORY \\
        -features TO_PREDICT \\
        -sources f=TESTING_DATA_SOURCE_TYPE \\
        -source-filename TESTING_DATA_FILE_NAME \\
        -scorer ACCURACY_SCORER \\
        -log debug

Predicting with trained model:

.. code-block:: console

    $ dffml predict all \\
        -model SCIKIT_MODEL_ENTRYPOINT \\
        -model-features FEATURE_DEFINITION \\
        -model-predict TO_PREDICT \\
        -model-location MODEL_DIRECTORY \\
        -sources f=PREDICT_DATA_SOURCE_TYPE \\
        -source-filename PREDICT_DATA_FILE_NAME \\
        -log debug


**Models Available:**

+----------------+-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
| Type           | Model                         | Entrypoint     | Parameters                                                                                                                                                                                    | Multi-Output             |
+================+===============================+================+===============================================================================================================================================================================================+==========================+
| Regression     | LinearRegression              | scikitlr       | `scikitlr <https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html#sklearn.linear_model.LinearRegression/>`_                                             |           Yes            |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | ElasticNet                    | scikiteln      | `scikiteln <https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.ElasticNet.html#sklearn.linear_model.ElasticNet/>`_                                                        |           Yes            |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | RandomForestRegressor         | scikitrfr      | `scikitrfr <https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html>`_                                                                                  |           Yes            |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | BayesianRidge                 | scikitbyr      | `scikitbyr <https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.BayesianRidge.html#sklearn.linear_model.BayesianRidge/>`_                                                  |           Yes            |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | Lasso                         | scikitlas      | `scikitlas <https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html#sklearn.linear_model.Lasso/>`_                                                                  |           Yes            |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | ARDRegression                 | scikitard      | `scikitard <https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.ARDRegression.html#sklearn.linear_model.ARDRegression/>`_                                                  |           Yes            |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | RANSACRegressor               | scikitrsc      | `scikitrsc <https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.RANSACRegressor.html#sklearn.linear_model.RANSACRegressor/>`_                                              |           Yes            |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | DecisionTreeRegressor         | scikitdtr      | `scikitdtr <https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeRegressor.html#sklearn.tree.DecisionTreeRegressor/>`_                                                  |           Yes            |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | GaussianProcessRegressor      | scikitgpr      | `scikitgpr <https://scikit-learn.org/stable/modules/generated/sklearn.gaussian_process.GaussianProcessRegressor.html#sklearn.gaussian_process.GaussianProcessRegressor/>`_                    |           Yes            |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | OrthogonalMatchingPursuit     | scikitomp      | `scikitomp <https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.OrthogonalMatchingPursuit.html#sklearn.linear_model.OrthogonalMatchingPursuit/>`_                          |           Yes            |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | Lars                          | scikitlars     | `scikitlars <https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lars.html#sklearn.linear_model.Lars/>`_                                                                   |           Yes            |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | Ridge                         | scikitridge    | `scikitridge <https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html#sklearn.linear_model.Ridge/>`_                                                                |           Yes            |
+----------------+-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
| Classification | KNeighborsClassifier          | scikitknn      | `scikitknn <https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.KNeighborsClassifier.html#sklearn.neighbors.KNeighborsClassifier/>`_                                          |           Yes            |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | AdaBoostClassifier            | scikitadaboost | `scikitadaboost <https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.AdaBoostClassifier.html#sklearn.ensemble.AdaBoostClassifier/>`_                                           |           Yes            |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | GaussianProcessClassifier     | scikitgpc      | `scikitgpc <https://scikit-learn.org/stable/modules/generated/sklearn.gaussian_process.GaussianProcessClassifier.html#sklearn.gaussian_process.GaussianProcessClassifier/>`_                  |           Yes            |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | DecisionTreeClassifier        | scikitdtc      | `scikitdtc <https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html#sklearn.tree.DecisionTreeClassifier/>`_                                                |           Yes            |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | RandomForestClassifier        | scikitrfc      | `scikitrfc <https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html#sklearn.ensemble.RandomForestClassifier/>`_                                        |           Yes            |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | QuadraticDiscriminantAnalysis | scikitqda      | `scikitqda <https://scikit-learn.org/stable/modules/generated/sklearn.discriminant_analysis.QuadraticDiscriminantAnalysis.html#sklearn.discriminant_analysis.QuadraticDiscriminantAnalysis/>`_|           Yes            |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | MLPClassifier                 | scikitmlp      | `scikitmlp <https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPClassifier.html#sklearn.neural_network.MLPClassifier/>`_                                              |           Yes            |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | GaussianNB                    | scikitgnb      | `scikitgnb <https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.GaussianNB.html#sklearn.naive_bayes.GaussianNB/>`_                                                          |           Yes            |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | SVC                           | scikitsvc      | `scikitsvc <https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html#sklearn.svm.SVC/>`_                                                                                        |           Yes            |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | LogisticRegression            | scikitlor      | `scikitlor <https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html#sklearn.linear_model.LogisticRegression/>`_                                        |           Yes            |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | GradientBoostingClassifier    | scikitgbc      | `scikitgbc <https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.GradientBoostingClassifier.html#sklearn.ensemble.GradientBoostingClassifier/>`_                                |           Yes            |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | BernoulliNB                   | scikitbnb      | `scikitbnb <https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.BernoulliNB.html#sklearn.naive_bayes.BernoulliNB/>`_                                                        |           Yes            |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | ExtraTreesClassifier          | scikitetc      | `scikitetc <https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html#sklearn.ensemble.ExtraTreesClassifier/>`_                                            |           Yes            |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | BaggingClassifier             | scikitbgc      | `scikitbgc <https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.BaggingClassifier.html#sklearn.ensemble.BaggingClassifier/>`_                                                  |           Yes            |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | LinearDiscriminantAnalysis    | scikitlda      | `scikitlda <https://scikit-learn.org/stable/modules/generated/sklearn.discriminant_analysis.LinearDiscriminantAnalysis.html#sklearn.discriminant_analysis.LinearDiscriminantAnalysis/>`_      |           Yes            |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | MultinomialNB                 | scikitmnb      | `scikitmnb <https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.MultinomialNB.html#sklearn.naive_bayes.MultinomialNB/>`_                                                    |           Yes            |
+----------------+-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
| Clustering     | KMeans                        | scikitkmeans   | `scikitkmeans <https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html#sklearn.cluster.KMeans/>`_                                                                       |           No             |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | Birch                         | scikitbirch    | `scikitbirch <https://scikit-learn.org/stable/modules/generated/sklearn.cluster.Birch.html#sklearn.cluster.Birch/>`_                                                                          |           No             |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | MiniBatchKMeans               | scikitmbkmeans | `scikitmbkmeans <https://scikit-learn.org/stable/modules/generated/sklearn.cluster.MiniBatchKMeans.html#sklearn.cluster.MiniBatchKMeans/>`_                                                   |           No             |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | AffinityPropagation           | scikitap       | `scikitap <https://scikit-learn.org/stable/modules/generated/sklearn.cluster.AffinityPropagation.html#sklearn.cluster.AffinityPropagation/>`_                                                 |           No             |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | MeanShift                     | scikitms       | `scikitms <https://scikit-learn.org/stable/modules/generated/sklearn.cluster.MeanShift.html#sklearn.cluster.MeanShift/>`_                                                                     |           No             |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | SpectralClustering            | scikitsc       | `scikitsc <https://scikit-learn.org/stable/modules/generated/sklearn.cluster.SpectralClustering.html#sklearn.cluster.SpectralClustering/>`_                                                   |           No             |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | AgglomerativeClustering       | scikitac       | `scikitac <https://scikit-learn.org/stable/modules/generated/sklearn.cluster.AgglomerativeClustering.html#sklearn.cluster.AgglomerativeClustering/>`_                                         |           No             |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | OPTICS                        | scikitoptics   | `scikitoptics <https://scikit-learn.org/stable/modules/generated/sklearn.cluster.OPTICS.html#sklearn.cluster.OPTICS/>`_                                                                       |           No             |
+----------------+-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+


**Scorers Available:**

+----------------+------------------------------------+--------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
| Type           | Scorer                             | Entrypoint         | Parameters                                                                                                                                                                           | Multi-Output             |
+================+====================================+====================+======================================================================================================================================================================================+==========================+
| Regression     | Explained Variance Score           | exvscore           | `exvscore <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.explained_variance_score.html#sklearn.metrics.explained_variance_score/>`_                              |           Yes            |
|                +------------------------------------+--------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | Max Error                          | maxerr             | `maxerr <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.max_error.html#sklearn.metrics.max_error/>`_                                                              |           No             |
|                +------------------------------------+--------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | Mean Absolute Error                | meanabserr         | `meanabserr <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.mean_absolute_error.html#sklearn.metrics.mean_absolute_error/>`_                                      |           Yes            |
|                +------------------------------------+--------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | Mean Squared Error                 | meansqrerr         | `meansqrerr <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.mean_squared_error.html#sklearn.metrics.mean_squared_error/>`_                                        |           Yes            |
|                +------------------------------------+--------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | Mean Squared Log Error             | meansqrlogerr      | `meansqrlogerr <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.mean_squared_log_error.html#sklearn.metrics.mean_squared_log_error/>`_                             |           Yes            |
|                +------------------------------------+--------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | Median Absolute Error              | medabserr          | `medabserr <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.median_absolute_error.html#sklearn.metrics.median_absolute_error/>`_                                   |           Yes            |
|                +------------------------------------+--------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | R2 Score                           | r2score            | `r2score <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.r2_score.html#sklearn.metrics.r2_score/>`_                                                               |           Yes            |
|                +------------------------------------+--------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | Mean Poisson Deviance              | meanpoidev         | `meanpoidev <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.mean_poisson_deviance.html#sklearn.metrics.mean_poisson_deviance/>`_                                  |           No             |
|                +------------------------------------+--------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | Mean Gamma Deviance                | meangammadev       | `meangammadev <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.mean_gamma_deviance.html#sklearn.metrics.mean_gamma_deviance/>`_                                    |           No             |
|                +------------------------------------+--------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | Mean Absolute Percentage Error     | meanabspererr      | `meanabspererr <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.mean_absolute_percentage_error.html#sklearn.metrics.mean_absolute_percentage_error/>`_             |           Yes            |
+----------------+------------------------------------+--------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
| Classification | Accuracy Score                     | acscore            | `acscore <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.accuracy_score.html#sklearn.metrics.accuracy_score/>`_                                                   |           Yes            |
|                +------------------------------------+--------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | Balanced Accuracy Score            | bacscore           | `bacscore <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.balanced_accuracy_score.html#sklearn.metrics.balanced_accuracy_score/>`_                                |           Yes            |
|                +------------------------------------+--------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | Top K Accuracy Score               | topkscore          | `topkscore <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.top_k_accuracy_score.html#sklearn.metrics.top_k_accuracy_score/>`_                                     |           Yes            |
|                +------------------------------------+--------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | Average Precision Score            | avgprescore        | `avgprescore <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html#sklearn.metrics.average_precision_score/>`_                             |           Yes            |
|                +------------------------------------+--------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | Brier Score Loss                   | brierscore         | `brierscore <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.brier_score_loss.html#sklearn.metrics.brier_score_loss/>`_                                            |           Yes            |
|                +------------------------------------+--------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | F1 Score                           | f1score            | `f1score <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.f1_score.html#sklearn.metrics.f1_score/>`_                                                               |           Yes            |
|                +------------------------------------+--------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | Log Loss                           | logloss            | `logloss <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.log_loss.html#sklearn.metrics.log_loss/>`_                                                               |           Yes            |
|                +------------------------------------+--------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | Precision Score                    | prescore           | `prescore <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_score.html#sklearn.metrics.precision_score/>`_                                                |           Yes            |
|                +------------------------------------+--------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | Recall Score                       | recallscore        | `recallscore <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.recall_score.html#sklearn.metrics.recall_score/>`_                                                   |           Yes            |
|                +------------------------------------+--------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | Jaccard Score                      | jacscore           | `jacscore <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.jaccard_score.html#sklearn.metrics.jaccard_score/>`_                                                    |           Yes            |
|                +------------------------------------+--------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | Roc Auc Score                      | rocaucscore        | `rocaucscore <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html#sklearn.metrics.roc_auc_score/>`_                                                 |           Yes            |
+----------------+------------------------------------+--------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
| Clustering     | Adjusted Mutual Info Score         | adjmutinfoscore    | `adjmutinfoscore <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.adjusted_mutual_info_score.html#sklearn.metrics.adjusted_mutual_info_score/>`_                   |           No             |
|                +------------------------------------+--------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | Adjusted Rand Score                | adjrandscore       | `adjrandscore <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.adjusted_rand_score.html#sklearn.metrics.adjusted_rand_score/>`_                                    |           No             |
|                +------------------------------------+--------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | Completeness Score                 | complscore         | `complscore <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.completeness_score.html#sklearn.metrics.completeness_score/>`_                                        |           No             |
|                +------------------------------------+--------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | Fowlkes Mallows Score              | fowlmalscore       | `fowlmalscore <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.fowlkes_mallows_score.html#sklearn.metrics.fowlkes_mallows_score/>`_                                |           No             |
|                +------------------------------------+--------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | Homogeneity Score                  | homoscore          | `homoscore <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.homogeneity_score.html#sklearn.metrics.homogeneity_score/>`_                                           |           No             |
|                +------------------------------------+--------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | Mutual Info Score                  | mutinfoscore       | `mutinfoscore <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.mutual_info_score.html#sklearn.metrics.mutual_info_score/>`_                                        |           No             |
|                +------------------------------------+--------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | Normalized Mutual Info Score       | normmutinfoscore   | `normmutinfoscore <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.normalized_mutual_info_score.html#sklearn.metrics.normalized_mutual_info_score/>`_              |           No             |
|                +------------------------------------+--------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | Rand Score                         | randscore          | `randscore <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.rand_score.html#sklearn.metrics.rand_score/>`_                                                         |           No             |
|                +------------------------------------+--------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
|                | V Measure Score                    | vmscore            | `vmscore <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.v_measure_score.html#sklearn.metrics.v_measure_score/>`_                                                 |           No             |
+----------------+------------------------------------+--------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+
| Supervised     | Model's Default Score              | skmodelscore       | `skmodelscore <https://scikit-learn.org/stable/modules/model_evaluation.html/>`_                                                                                                     |           Yes            |
+----------------+------------------------------------+--------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------+


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
        -model-location tempdir \\
        -sources f=csv \\
        -source-filename train.csv \\
        -source-readonly \\
        -log debug
    $ dffml accuracy \\
        -model scikitkmeans \\
        -model-features Col1:float:1 Col2:float:1 Col3:float:1 Col4:float:1\\
        -model-predict cluster:int:1 \\
        -model-location tempdir \\
        -features cluster:int:1 \\
        -sources f=csv \\
        -source-filename test.csv \\
        -source-readonly \\
        -scorer skmodelscore \\
        -log debug
    0.6365141682948129
    $ echo -e 'Col1,Col2,Col3,Col4\\n6.09809669,8.36434181,6.70940915,-7.91491768\\n' | \\
      dffml predict all \\
        -model scikitkmeans \\
        -model-features Col1:float:1 Col2:float:1 Col3:float:1 Col4:float:1 \\
        -model-location tempdir \\
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

    from dffml import CSVSource, Features, Feature
    from dffml.noasync import train, score, predict
    from dffml_model_scikit import KMeansModel
    from dffml_model_scikit import MutualInfoScoreScorer

    model = KMeansModel(
        features=Features(
            Feature("Col1", float, 1),
            Feature("Col2", float, 1),
            Feature("Col3", float, 1),
            Feature("Col4", float, 1),
        ),
        predict=Feature("cluster", int, 1),
        location="tempdir",
    )

    # Train the model
    train(model, "train.csv")

    # Assess accuracy (alternate way of specifying data source)
    scorer = MutualInfoScoreScorer()
    print("Accuracy:", score(model, scorer, Feature("cluster", int, 1), CSVSource(filename="test.csv")))

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

- features: List of features

  - Features to train on

- location: Path

  - Location where state should be saved

"""
from .scikit_models import *
from .scikit_scorers import *
from .scikit_model_scorer import SklearnModelAccuracy, ScorerWillNotWork
