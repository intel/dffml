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
        -source-readonly \\
        -log debug

Testing and Accuracy:

.. code-block:: console

    $ dffml accuracy \\
        -model SCIKIT_MODEL_ENTRYPOINT \\
        -model-features FEATURE_DEFINITION \\
        -model-predict TO_PREDICT \\
        -sources f=TESTING_DATA_SOURCE_TYPE \\
        -source-filename TESTING_DATA_FILE_NAME \\
        -source-readonly \\
        -log debug

Predicting with trained model:

.. code-block:: console

    $ dffml predict all \\
        -model SCIKIT_MODEL_ENTRYPOINT \\
        -model-features FEATURE_DEFINITION \\
        -model-predict TO_PREDICT \\
        -sources f=PREDICT_DATA_SOURCE_TYPE \\
        -source-filename PREDICT_DATA_FILE_NAME \\
        -source-readonly \\
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


**Usage Example:**

Example below uses LinearRegression Model on a small dataset.

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

.. code-block:: console

    $ cat > train.csv << EOF
    Years,Expertise,Trust,Salary
    0,1,0.2,10
    1,3,0.4,20
    2,5,0.6,30
    3,7,0.8,40
    EOF
    $ cat > test.csv << EOF
    Years,Expertise,Trust,Salary
    4,9,1.0,50
    5,11,1.2,60
    EOF
    $ dffml train \\
        -model scikitlr \\
        -model-features def:Years:int:1 def:Expertise:int:1 def:Trust:float:1 \\
        -model-predict Salary \\
        -sources f=csv \\
        -source-filename train.csv \\
        -source-readonly \\
        -log debug
    $ dffml accuracy \\
        -model scikitlr \\
        -model-features def:Years:int:1 def:Expertise:int:1 def:Trust:float:1 \\
        -model-predict Salary \\
        -sources f=csv \\
        -source-filename test.csv \\
        -source-readonly \\
        -log debug
    1.0
    $ echo -e 'Years,Expertise,Trust\\n6,13,1.4\\n' | \\
      dffml predict all \\
        -model scikitlr \\
        -model-features def:Years:int:1 def:Expertise:int:1 def:Trust:float:1 \\
        -model-predict Salary \\
        -sources f=csv \\
        -source-filename /dev/stdin \\
        -source-readonly \\
        -log debug
    [
        {
            "extra": {},
            "features": {
                "Expertise": 13,
                "Trust": 1.4,
                "Years": 6
            },
            "last_updated": "2019-09-18T19:04:18Z",
            "prediction": {
                "confidence": 1.0,
                "value": 70.00000000000001
            },
            "src_url": 0
        }
    ]
"""
