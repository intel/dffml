import math
import pathlib
from typing import AsyncIterator, Type

import numpy as np

from dffml import (
    Accuracy,
    Feature,
    Features,
    ModelNotTrained,
    Record,
    SimpleModel,
    SourcesContext,
    config,
    entrypoint,
    field,
)


def split(a_list, k):
    L = int(k * len(a_list))
    return a_list[:L], a_list[L:]


def estimateGaussian(X):

    n = np.size(X, 1)
    m = np.size(X, 0)
    mu = np.zeros((n, 1))
    sigma2 = np.zeros((n, 1))

    mu = np.reshape((1 / m) * np.sum(X, 0), (1, n))
    sigma2 = np.reshape(((1 / m) * np.sum(np.square(X - mu), 0)), (1, n))
    return mu, sigma2


def multivariateGaussian(X, mu, sigma2):
    n = np.size(sigma2, 1)
    m = np.size(sigma2, 0)

    if n == 1 or m == 1:
        sigma2 = np.diag(sigma2[0, :])

    X = X - mu
    pi = math.pi
    det = np.linalg.det(sigma2)
    inv = np.linalg.inv(sigma2)
    val = np.reshape(
        (-0.5) * np.sum(np.multiply((X @ inv), X), 1), (np.size(X, 0), 1)
    )

    p = np.power(2 * pi, n / -2) * np.power(det, -0.5) * np.exp(val)

    return p


def findIndices(binVec):
    l = []
    for i in range(len(binVec)):
        if binVec[i] == 1:
            l.append(i)
    return l


def selectThreshold(Yval, pval):
    bestEpsilon = 0
    bestF1 = 0
    F1 = 0
    stepsize = (np.max(pval) - np.min(pval)) / 1000
    epsVec = np.arange(np.min(pval), np.max(pval), stepsize)
    lenv = len(epsVec)

    for eps in range(lenv):
        epsilon = epsVec[eps]
        pred = (pval < epsilon).astype(int)
        F1 = getF1(Yval, pred)
        if F1 > bestF1:
            bestF1 = F1
            bestEpsilon = epsilon

    return bestF1, bestEpsilon


def getF1(Yval, pred):
    prec, rec = 0, 0
    tp, fp, fn = 0, 0, 0

    try:
        fp = np.sum(((pred == 1) & (Yval == 0)).astype(int))
        tp = np.sum(((pred == 1) & (Yval == 1)).astype(int))
        fn = np.sum(((pred == 0) & (Yval == 1)).astype(int))

        prec = tp / (tp + fp)
        rec = tp / (tp + fn)
        F1 = 2 * prec * rec / (prec + rec)
    except ZeroDivisionError:
        raise
    return F1


@config
class AnomalyModelConfig:
    features: Features = field("Features to train on")
    predict: Feature = field("Label or the value to be predicted")
    directory: pathlib.Path = field("Directory where state should be saved")
    k: float = field("Validation set size", default=0.8)


@entrypoint("anomalydetection")
class AnomalyModel(SimpleModel):

    r"""
    Model for Anomaly Detection using multivariate Gaussian distribution to predict probabilities of all records in the dataset
    and identify outliers. F1 score is used as the evaluation metric for this model. This model works well as it recognises dependencies
    across various features, and works particularly well if the features have a Gaussian Distribution.

    Examples
    --------

    Command line usage

    Create training and test datasets

    **trainex.csv**

    .. code-block::
        :test:
        :filepath: trainex.csv

        A,Y
        0.65,0
        0.24,0
        0.93,0
        0.87,0
        0.23,0
        7,1
        0.86,0
        0.45,0
        0.55,0
        0.29,0
        5,1
        0.51,0
        0.88,0
        0.24,0
        0.51,0
        0.17,0
        9,1
        0.37,0
        0.23,0
        0.44,0
        0.62,0
        3,1
        0.87,0

    **testex.csv**

    .. code-block::
        :test:
        :filepath: testex.csv

        A,Y
        0.45,0
        0.23,0
        0.67,0
        8,1
        0.19,0
        0.34,0
        0.49,0
        0.31,0
        0.47,0
        4,1

    Train the model

    .. code-block:: console
        :test:


        $ dffml train \
            -sources f=csv \
            -source-filename trainex.csv \
            -model anomalydetection \
            -model-features A:float:2 \
            -model-predict Y:int:1  \
            -model-directory tempdir

    Assess the accuracy

    .. code-block:: console
        :test:

        $ dffml accuracy \
            -sources f=csv \
            -source-filename testex.csv \
            -model anomalydetection \
            -model-features A:float:2 \
            -model-predict Y:int:1 \
            -model-directory tempdir


    Make predictions

    .. code-block:: console
        :test:

        $ dffml predict all \
            -sources f=csv \
            -source-filename testex.csv \
            -model anomalydetection \
            -model-features A:float:2 \
            -model-predict Y:int:1 \
            -model-directory tempdir


    Python usage

    .. literalinclude:: /../model/scratch/examples/anomalydetection_ex/detectoutliers.py
        :test:


    Output

    .. code-block:: console
        :test:

        $ python detectoutliers.py
        Test set F1 score : 0.8
        Training set F1 score : 0.888888888888889

    """

    # The configuration class needs to be set as the CONFIG property
    CONFIG: Type = AnomalyModelConfig

    async def train(self, sources: SourcesContext) -> None:
        # Number of features
        nof = len(self.features)
        # X and Y data
        X = []
        Y = []
        # Go through all records that have the feature we're training on and the
        # feature we want to predict.
        async for record in sources.with_features(
            self.features + [self.parent.config.predict.name]
        ):
            record_data = []
            for feature in record.features(self.features).values():
                record_data.extend(
                    [feature] if np.isscalar(feature) else feature
                )

            X.append(record_data)
            Y.append(record.feature(self.parent.config.predict.name))

        k = self.parent.config.k
        X1, Xval = split(X, k)
        X = X1
        Y1, Yval = split(Y, k)
        Y = Y1

        X = np.reshape(X, (len(X), nof))
        Xval = np.reshape(Xval, (len(Xval), nof))
        Y = np.reshape(Y, (len(Y), 1))
        Yval = np.reshape(Yval, (len(Yval), 1))

        # Use self.logger to report how many records are being used for training
        self.logger.debug("Number of training records: %d", len(X))
        self.logger.debug("Number of records in validation set: %d", len(Xval))

        mu, sigma2 = estimateGaussian(X)
        p = multivariateGaussian(X, mu, sigma2)

        pval = multivariateGaussian(Xval, mu, sigma2)

        F1val, epsilon = selectThreshold(Yval, pval)

        outliers = p < epsilon

        # Outliers in training set
        listOfOl = findIndices(outliers)

        # Save epsilon and F1 score
        self.storage["anomalies"] = (
            epsilon,
            F1val,
            mu.tolist(),
            sigma2.tolist(),
        )

    async def accuracy(self, sources: SourcesContext) -> Accuracy:
        # Load saved anomalies
        anomalies = self.storage.get("anomalies", None)
        # Ensure the model has been trained before we try to make a prediction
        if anomalies is None:
            raise ModelNotTrained("Train model before assessing for accuracy.")

        epsilon, _F1val, mu, sigma2 = anomalies

        X = []
        Y = []
        # Go through all records that have the feature we're training on and the
        # feature we want to predict.
        async for record in sources.with_features(
            self.features + [self.parent.config.predict.name]
        ):
            record_data = []
            for feature in record.features(self.features).values():
                record_data.extend(
                    [feature] if np.isscalar(feature) else feature
                )

            X.append(record_data)
            Y.append(record.feature(self.parent.config.predict.name))

        self.logger.debug("Number of test records: %d", len(X))

        # Number of features
        nof = len(self.features)

        X = np.reshape(X, (len(X), nof))

        Y = np.reshape(Y, (len(Y), 1))

        mu = np.array(mu)
        sigma2 = np.array(sigma2)
        p = multivariateGaussian(X, mu, sigma2)

        pred = (p < epsilon).astype(int)

        F1 = getF1(Y, pred)

        outliers = p < epsilon

        listOfOl = findIndices(outliers)

        accuracy = F1
        # Update the accuracy
        self.storage["anomalies"] = epsilon, F1, mu.tolist(), sigma2.tolist()
        return Accuracy(accuracy)

    async def get_input_data(self, sources: SourcesContext) -> list:
        saved_records = []
        async for record in sources.with_features(
            self.config.features.names()
        ):
            saved_records.append(record)
        return saved_records

    async def predict(self, sources: SourcesContext) -> AsyncIterator[Record]:

        # Load saved anomalies
        anomalies = self.storage.get("anomalies", None)
        # Ensure the model has been trained before we try to make a prediction
        if anomalies is None:
            raise ModelNotTrained("Train model before prediction")
        # Expand the anomalies into named variables
        epsilon, F1, mu, sigma2 = anomalies
        mu = np.array(mu)
        sigma2 = np.array(sigma2)
        # Grab records and input data (X data)
        input_data = await self.get_input_data(sources)
        # Make predictions
        X = []
        for record in input_data:
            record_data = []
            for feature in record.features(self.features).values():
                record_data.extend(
                    [feature] if np.isscalar(feature) else feature
                )
            X.append(record_data)
        p = multivariateGaussian(X, mu, sigma2)
        predictions = (p < epsilon).astype(int)
        for record, prediction in zip(input_data, predictions):
            record.predicted(
                self.config.predict.name, int(prediction), float(F1)
            )
            yield record
