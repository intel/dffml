"""
Machine Learning models implemented with `scikit-learn <https://scikit-learn.org/stable/>`_.
Models are saved under the directory in subdirectories named after the hash of
their feature names.

**General Usage:**

Training:

.. code-block:: console

    $ dffml train \\
        -model SCIKIT_MODEL_ENTRYPOINT \\
        -features FEATURE_DEFINITION \\
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
        -features FEATURE_DEFINITION \\
        -model-predict TO_PREDICT \\
        -sources f=TESTING_DATA_SOURCE_TYPE \\
        -source-filename TESTING_DATA_FILE_NAME \\
        -source-readonly \\
        -log debug

Predicting with trained model:

.. code-block:: console

    $ dffml predict all \\
        -model SCIKIT_MODEL_ENTRYPOINT \\
        -features FEATURE_DEFINITION \\
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
        -features def:Years:int:1 def:Expertise:int:1 def:Trust:float:1 \\
        -model-predict Salary \\
        -sources f=csv \\
        -source-filename train.csv \\
        -source-readonly \\
        -log debug
    $ dffml accuracy \\
        -model scikitlr \\
        -features def:Years:int:1 def:Expertise:int:1 def:Trust:float:1 \\
        -model-predict Salary \\
        -sources f=csv \\
        -source-filename test.csv \\
        -source-readonly \\
        -log debug
    1.0
    $ echo -e 'Years,Expertise,Trust\\n6,13,1.4\\n' | \\
      dffml predict all \\
        -model scikitlr \\
        -features def:Years:int:1 def:Expertise:int:1 def:Trust:float:1 \\
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
