import math
import pathlib
import statistics
from typing import AsyncIterator, Type

import numpy as np
from dffml import (Accuracy, Feature, ModelNotTrained, Record, SimpleModel,
                   SourcesContext, config, entrypoint, field)


@config
class AnomalyModelConfig:
    feature: Feature = field("Feature to train on")
    predict: Feature = field("Label or the value to be predicted")
    directory: pathlib.Path = field("Directory where state should be saved")


@entrypoint("anomalydetection")
class AnomalyModel(SimpleModel):
    # The configuration class needs to be set as the CONFIG property
    CONFIG: Type = AnomalyModelConfig


def estimateGaussian(X):
    n = np.size(X, 1)
    m = np.size(X, 0)
    mu = np.zeros((n, 1))
    sigma2 = np.zeros((n, 1))

    mu = np.reshape((1 / m) * np.sum(X, 0), (1, n))
    sigma2 = np.reshape(((1 / m) * np.sum(np.square(X - mu), 0)), (1, n))
    return mu, sigma2


def multivariateGaussian(X, mu, sigma2):
    if (np.size(sigma2, 1) == 1) | (np.size(sigma2, 1) == 1):
        sigma2 = np.diag(sigma2[0, :])

    X = X - mu
    pi = math.pi
    det = np.linalg.det(sigma2)
    inv = np.linalg.inv(sigma2)
    val = np.reshape((-0.5) * np.sum(np.multiply((X @ inv), X), 1), (np.size(X, 0), 1))
    # @ does element wise martix multiplication
    p = np.power(2 * pi, -n / 2) * np.power(det, -0.5) * np.exp(val)

    return p


def split(a_list):
    L = int(0.9 * len(a_list))
    return a_list[:L], a_list[L:]


def selectThreshold(Yval, pval):
    bestEpsilon = 0
    bestF1 = 0
    F1 = 0
    stepsize = (np.max(pval) - np.min(pval)) / 1000
    epsVec = np.arange(np.min(pval), np.max(pval), stepsize)
    lenv = len(epsVec)

    for eps in range(lenv):
        epsilon = epsVec[eps]
        pred = pval < epsilon
        prec, rec = 0, 0
        tp, fp, fn = 0, 0, 0

        try:
            fp = np.sum(((pred == 1) & (Yval == 0)).astype(int))
            tp = np.sum(((pred == 1) & (Yval == 1)).astype(int))
            fn = np.sum(((pred == 0) & (Yval == 1)).astype(int))

            prec = tp / (tp + fp)
            rec = tp / (tp + fn)
            F1 = 2 * prec * rec / (prec + rec)
            if F1 > bestF1:
                bestF1 = F1
                bestEpsilon = epsilon
        except ZeroDivisionError:
            print("Warning : dividing by zero!")

    return bestF1, bestEpsilon


def findIndices(binVec):
    l = []
    for i in range(len(binVec)):
        if binVec[i] == 1:
            l.append(i)
    return l


async def train(self, sources: SourcesContext) -> None:
    # X and Y data
    X = []
    Y = []
    # Go through all records that have the feature we're training on and the
    # feature we want to predict.
    async for record in sources.with_features(
        [self.config.feature.name, self.config.predict.name]
    ):
        X.append(record.feature(self.config.feature.name))
        Y.append(record.feature(self.config.predict.name))

    X1, Xval = split(X)
    X = X1
    Y1, Yval = split(Y)
    Y = Y1

    # Use self.logger to report how many records are being used for training
    self.logger.debug("Number of training records: %d", len(X))
    self.logger.debug("Number of records in validation set: %d", len(Xval))

    mu, sigma2 = estimateGaussian(X)
    p = multivariateGaussian(X, mu, sigma2)

    pval = multivariateGaussian(Xval, mu, sigma2)

    F1, epsilon = selectThreshold(Yval, pval)

    outliers = p < epsilon

    listOfOl = findIndices(outliers)

    # Save listOfOl and F1 score
    self.storage["anomalies"] = listOfOl, F1


async def accuracy(self, sources: SourcesContext) -> Accuracy:
    # Load saved anomalies
    anomalies = self.storage.get("anomalies", None)
    # Ensure the model has been trained before we try to make a prediction
    if anomalies is None:
        raise ModelNotTrained("Train model before assessing for accuracy.")
    # F1 is the last element in anomalies, which is a list of
    # two values: listOfOl and F1
    return Accuracy(anomalies[1])


async def predict(self, sources: SourcesContext) -> AsyncIterator[Record]:
    # Load saved anomalies
    anomalies = self.storage.get("anomalies", None)
    # Ensure the model has been trained before we try to make a prediction
    if anomalies is None:
        raise ModelNotTrained("Train model before prediction")
    # Expand the anomalies into named variables
    listOfOl, F1 = anomalies
    # Iterate through each record that needs a prediction
    i = 0
    async for record in sources.with_features([self.config.feature.name]):
        # Grab the x data from the record
        x = record.feature(self.config.feature.name)
        # Calculate y
        if i in listOfOl:
            y = 1
        else:
            y = 0
        # Set the calculated value with the estimated accuracy
        record.predicted(self.config.predict.name, y, accuracy)
        # Yield the record to the caller
        i = i + 1
        yield record
