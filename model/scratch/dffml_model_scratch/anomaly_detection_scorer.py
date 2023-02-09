from dffml.feature.feature import Feature
import numpy as np

from dffml.base import config
from dffml.source.source import Sources
from dffml.util.entrypoint import entrypoint
from dffml.model import ModelNotTrained, ModelContext
from dffml.feature.feature import Feature
from dffml.accuracy import (
    AccuracyScorer,
    AccuracyContext,
)

from dffml_model_scratch.anomalydetection import (
    getF1,
    multivariateGaussian,
    findIndices,
)


@config
class AnomalyDetectionAccuracyConfig:
    pass


class AnomalyDetectionAccuracyContext(AccuracyContext):
    """
    Scorer for getting the accuracy of the Anomaly Detection model
    """

    async def score(
        self, mctx: ModelContext, sctx: Sources, features: Feature
    ):
        # Load saved anomalies
        anomalies = mctx.storage.get("anomalies", None)
        # Ensure the model has been trained before we try to make a prediction
        if not mctx.is_trained:
            raise ModelNotTrained("Train model before assessing for accuracy.")

        epsilon, _F1val, mu, sigma2 = anomalies

        X = []
        Y = []
        # Go through all records that have the feature we're training on and the
        # feature we want to predict.
        async for record in sctx.with_features(
            mctx.features + [features.name]
        ):
            record_data = []
            for feature in record.features(mctx.features).values():
                record_data.extend(
                    [feature] if np.isscalar(feature) else feature
                )

            X.append(record_data)
            Y.append(record.feature(features.name))

        mctx.logger.debug("Number of test records: %d", len(X))

        # Number of features
        nof = len(mctx.features)

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
        mctx.storage["anomalies"] = epsilon, F1, mu.tolist(), sigma2.tolist()
        return accuracy


@entrypoint("anomalyscore")
class AnomalyDetectionAccuracy(AccuracyScorer):
    CONFIG = AnomalyDetectionAccuracyConfig
    CONTEXT = AnomalyDetectionAccuracyContext
