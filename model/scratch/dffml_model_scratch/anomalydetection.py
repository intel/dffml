import math
import pathlib
import statistics
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
    L = int(k * len(a_list))  # validation set is currently at 20% of training set
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
    # print(m,n)

    if n == 1 or m == 1:
        sigma2 = np.diag(sigma2[0, :])

    X = X - mu
    pi = math.pi
    det = np.linalg.det(sigma2)
    inv = np.linalg.inv(sigma2)
    val = np.reshape((-0.5) * np.sum(np.multiply((X @ inv), X), 1), (np.size(X, 0), 1))
    # print(val.shape)
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
        print("Warning : dividing by zero!")

    return F1


@config
class AnomalyModelConfig:
    features: Features = field("Features to train on")
    predict: Feature = field("Label or the value to be predicted")
    directory: pathlib.Path = field("Directory where state should be saved")


@entrypoint("anomalydetection")
class AnomalyModel(SimpleModel):
    # The configuration class needs to be set as the CONFIG property
    CONFIG: Type = AnomalyModelConfig

    async def train(self, sources: SourcesContext) -> None:
        k = 0.7  # validation set size, currently set to 20% of training set size
        nof = len(self.features)  # number of features
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
                record_data.extend([feature] if np.isscalar(feature) else feature)

            X.append(record_data)
            Y.append(record.feature(self.parent.config.predict.name))

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

        listOfOl = findIndices(outliers)  # outliers in training set
        # print(F1val)
        # Save listOfOl and F1 score
        self.storage["anomalies"] = (
            listOfOl,
            epsilon,
            F1val,
        )

    async def accuracy(self, sources: SourcesContext) -> Accuracy:
        # Load saved anomalies
        anomalies = self.storage.get("anomalies", None)
        # Ensure the model has been trained before we try to make a prediction
        if anomalies is None:
            raise ModelNotTrained("Train model before assessing for accuracy.")

        listOfOl, epsilon, _F1val = anomalies

        X = []
        Y = []
        # Go through all records that have the feature we're training on and the
        # feature we want to predict.
        async for record in sources.with_features(
            self.features + [self.parent.config.predict.name]
        ):
            record_data = []
            for feature in record.features(self.features).values():
                record_data.extend([feature] if np.isscalar(feature) else feature)

            X.append(record_data)
            Y.append(record.feature(self.parent.config.predict.name))

        self.logger.debug("Number of test records: %d", len(X))

        nof = len(self.features)  # number of features

        X = np.reshape(X, (len(X), nof))

        Y = np.reshape(Y, (len(Y), 1))

        mu, sigma2 = estimateGaussian(X)

        p = multivariateGaussian(X, mu, sigma2)

        pred = (p < epsilon).astype(int)

        F1 = getF1(Y, pred)

        outliers = p < epsilon

        listOfOl = findIndices(outliers)

        # print(listOfOl)
        accuracy = F1
        # Update the accuracy, listOfOl
        self.storage["anomalies"] = listOfOl, epsilon, F1
        return Accuracy(accuracy)


"""    
    async def get_input_data(self, sources: SourcesContext) -> list:
        saved_records = []
        async for record in sources.with_features(self.config.features.names()):
            saved_records.append(record)
        return saved_records

    async def predict(self, sources: SourcesContext) -> AsyncIterator[Record]:

        # Load saved anomalies
        anomalies = self.storage.get("anomalies", None)
        # Ensure the model has been trained before we try to make a prediction
        if anomalies is None:
            raise ModelNotTrained("Train model before prediction")
        # Expand the anomalies into named variables
        listOfOl, epsilon, F1 = anomalies
        # Grab records and input data (X data)
        input_data = await self.get_input_data(sources)
        # Make predictions
        
        for record in input_data:
            record_data = []
            for feature in record.features(self.features).values():
                record_data.extend([feature] if np.isscalar(feature) else feature)
            p = multivariateGaussian()
            if p < epsilon:
                y = 1
            else:
                y = 0
            record.predicted(self.config.predict.name, y, F1)
            
            yield record
"""
