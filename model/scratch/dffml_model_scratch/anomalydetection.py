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

        def split(a_list):
            L = int(0.7 * len(a_list))
            return a_list[:L], a_list[L:]

        X1, Xval = split(X)
        X = X1
        Y1, Yval = split(Y)
        Y = Y1

        X = np.reshape(X, (len(X), 2))  # replace 2 by number of features
        Xval = np.reshape(
            Xval, (len(Xval), 2)
        )  # replace 2 by number of features
        Y = np.reshape(Y, (len(Y), 1))
        Yval = np.reshape(Yval, (len(Yval), 1))

        # Use self.logger to report how many records are being used for training
        self.logger.debug("Number of training records: %d", len(X))
        self.logger.debug("Number of records in validation set: %d", len(Xval))

        def estimateGaussian(X):

            n = np.size(X, 1)
            m = np.size(X, 0)
            mu = np.zeros((n, 1))
            sigma2 = np.zeros((n, 1))

            mu = np.reshape((1 / m) * np.sum(X, 0), (1, n))
            sigma2 = np.reshape(
                ((1 / m) * np.sum(np.square(X - mu), 0)), (1, n)
            )
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
            val = np.reshape(
                (-0.5) * np.sum(np.multiply((X @ inv), X), 1),
                (np.size(X, 0), 1),
            )
            # print(val.shape)
            p = np.power(2 * pi, n / -2) * np.power(det, -0.5) * np.exp(val)

            return p

        """def selectThreshold(yval, pval):
            F1 = 0
            bestF1 = 0
            bestEpsilon = 0

            stepsize = (np.max(pval) - np.min(pval)) / 1000

            epsVec = np.arange(np.min(pval), np.max(pval), stepsize)
            noe = len(epsVec)

            for eps in range(noe):
                epsilon = epsVec[eps]
                pred = pval < epsilon
                prec, rec = 0, 0
                tp, fp, fn = 0, 0, 0

                try:
                    for i in range(np.size(pval, 0)):
                        if pred[i] == 1 and yval[i] == 1:
                            tp += 1
                        elif pred[i] == 1 and yval[i] == 0:
                            fp += 1
                        elif pred[i] == 0 and yval[i] == 1:
                            fn += 1
                    prec = tp / (tp + fp)
                    rec = tp / (tp + fn)
                    F1 = 2 * prec * rec / (prec + rec)
                    if F1 > bestF1:
                        bestF1 = F1
                        bestEpsilon = epsilon
                except ZeroDivisionError:
                    print("Warning dividing by zero!!")

            return bestF1, bestEpsilon, prec,rec"""

        def findIndices(binVec):
            l = []
            for i in range(len(binVec)):
                if binVec[i] == 1:
                    l.append(i)
            return l

        """def getF1(outliers, Y):
            tp,fn,fp = 0,0,0
            for i in range(np.size(outliers, 0)):
                if outliers[i] == 1 and Y[i] == 1:
                    tp += 1
                elif outliers[i] == 1 and Y[i] == 0:
                    fp += 1
                elif outliers[i] == 0 and Y[i] == 1:
                    fn += 1
            prec = tp / (tp + fp)
            rec = tp / (tp + fn)
            #F1 = 2 * prec * rec / (prec + rec)
            return prec,rec
"""

        def selectThreshold(Yval, pval):
            bestEpsilon = 0
            bestF1 = 0
            F1 = 0
            stepsize = (np.max(pval) - np.min(pval)) / 1000
            epsVec = np.arange(np.min(pval), np.max(pval), stepsize)
            lenv = len(epsVec)
            prec, rec = 0, 0
            bprec, brec = 0, 0
            tp, fp, fn = 0, 0, 0
            for eps in range(lenv):
                epsilon = epsVec[eps]
                pred = (pval < epsilon).astype(int)

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

        mu, sigma2 = estimateGaussian(X)
        p = multivariateGaussian(X, mu, sigma2)

        pval = multivariateGaussian(Xval, mu, sigma2)

        F1val, epsilon = selectThreshold(Yval, pval)

        outliers = p < epsilon

        outval = pval < epsilon

        listVal = findIndices(outval)

        listVal = [z + len(X) for z in listVal]  # outliers in validation set

        listOfOl = findIndices(outliers)  # outliers in training set

        F1train, dummy = selectThreshold(Y, p)

        # Save listOfOl and F1 score
        self.storage["anomalies"] = (
            (listOfOl + listVal),
            (0.7 * F1train) + (0.3 * F1val),
        )
        print(F1train)
        print(F1val)
        print(listOfOl + listVal)

    async def accuracy(self, sources: SourcesContext) -> Accuracy:
        # Load saved anomalies
        anomalies = self.storage.get("anomalies", None)
        # Ensure the model has been trained before we try to make a prediction
        if anomalies is None:
            raise ModelNotTrained("Train model before assessing for accuracy.")
        # F1 is the last element in anomalies, which is a list of
        # two values: listOfOl and F1
        return Accuracy(anomalies[1])


"""
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
            record.predicted(self.config.predict.name, y, F1)
            # Yield the record to the caller
            i = i + 1
            yield record
"""
