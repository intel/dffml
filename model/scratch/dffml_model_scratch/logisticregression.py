import pathlib
import importlib
from typing import AsyncIterator, Tuple, Any

from dffml import (
    config,
    field,
    entrypoint,
    SimpleModel,
    ModelNotTrained,
    Accuracy,
    Feature,
    Features,
    Sources,
    Record,
    SourcesContext,
)

from autograd import grad
import autograd.numpy as np
import matplotlib.pyplot as plt
from scipy.stats import multivariate_normal as mvn


@config
class LogisticRegressionConfig:
    predict: Feature = field("Label or the value to be predicted")
    features: Features = field("Features to train on")
    directory: pathlib.Path = field("Directory where state should be saved")


@entrypoint("scratchlgrsag")
class LogisticRegression(SimpleModel):
    r"""
    Logistic Regression using stochastic average gradient descent optimizer

    The dataset used for training

    .. literalinclude:: /../model/scratch/examples/scratchlgrsag/dataset.sh

    Train the model

    .. literalinclude:: /../model/scratch/examples/scratchlgrsag/train.sh

    Assess the accuracy

    .. literalinclude:: /../model/scratch/examples/scratchlgrsag/accuracy.sh

    Output

    .. code-block:: console

        1.0

    Make a prediction

    .. literalinclude:: /../model/scratch/examples/scratchlgrsag/predict.sh

    Output

    .. code-block:: console

        [
            {
                "extra": {},
                "features": {
                    "ans": 0,
                    "f1": 0.8
                },
                "last_updated": "2020-03-19T13:41:08Z",
                "prediction": {
                    "ans": {
                        "confidence": 1.0,
                        "value": 1
                    }
                },
                "key": "0"
            }
        ]

    Example usage of Logistic Regression using Python

    .. literalinclude:: /../model/scratch/examples/scratchlgrsag/scratchlgrsag.py

    """
    # The configuration class needs to be set as the CONFIG property
    CONFIG = LogisticRegressionConfig
    # Logistic Regression only supports training on a single feature
    NUM_SUPPORTED_FEATURES = 1
    # We only support single dimensional values, non-matrix / array
    SUPPORTED_LENGTHS = [1]

    def __init__(self, config):
        super().__init__(config)
        self.np = importlib.import_module("numpy")
        # self.xData = self.np.array([])
        # self.yData = self.np.array([])

    """
    Perform a fixed number of iterations of gradient descent on a function using a fixed
    Input:
    fun : function handle: function that takes in a numpy array of shape (d,) and re
    x0 : initial point: numpy array of shape (d,)
    lr : fixed learning rate: a positive float
    iterations : number of iterations to perform: int

    Return:
    x : minimizer to fun: numpy array of shape (d,)
    """

    @property
    def separating_line(self):
        """
        Load separating_line from disk, if it hasn't been set yet, return None
        """
        return self.storage.get("separating_line", None)

    @separating_line.setter
    def separating_line(self, sline):
        """
        Set separating_line in self.storage so it will be saved to disk
        """
        self.storage["separating_line"] = sline

    def predict_input(self, x):
        """
        The Logistic regression with SAG optimizer: returns w * x + b > 0.5
        """
        prediction = self.separating_line[0] * x + self.separating_line[1]
        if prediction > 0.5:
            prediction = 1
        else:
            prediction = 0
        self.logger.debug(
            "Predicted Value of {} {}:".format(
                self.config.predict.name, prediction
            )
        )
        return prediction

    def make_data(n_samples = 500):
        # Generate data features.
        X1 = mvn.rvs(mean = np.array([1.1, 0]), cov = 0.2*np.eye(2), size = n_samples//2
        X2 = mvn.rvs(mean = np.array([-1.1, 0]), cov = 0.2*np.eye(2), size = n_samples -
        # Append data labels and combine.
        X1 = np.hstack( (X1, np.ones((X1.shape[0], 1))))
        X2 = np.hstack( (X2, np.zeros((X2.shape[0], 1))))
        X = np.vstack([X1, X2])
        # Randomly permute data.
        np.random.shuffle(X)
        return X

    def lr_update(lr, i):
        lr = lr / (i + 1)
        return lr
    
    def gd(fun, x0, lr):
        grad_fun = grad(fun)
        x = x0 - lr * grad_fun(x0)
        x0 = x
        return x

    def best_separating_line(self):
        """
        Determine the best separating hyperplane (here, the integer weight) 
        s.t. w * x + b is well separable from 0.5.
        """
        self.logger.debug(
            "Number of input records: {}".format(len(self.X))
        )

        np.random.seed(2)
        data = make_data()
        X = data[:,:-1] # Features
        y = data[:,-1] # Labels

        # We augment the data so that x_0 = 1 for the intercept term.
        X = np.append(np.ones((len(X), 1)), X, axis = 1)

        n_samples = len(X)
        train = int(n_samples * 0.4)
        val = int(n_samples * 0.8)

        X_train, y_train = X[:train], y[:train]
        X_val, y_val = X[train:val], y[train:val]
        X_test, y_test = X[val:], y[val:]

        iterations = 5000
        m = 10

        #x = self.xData  # feature array
        #y = self.yData  # class array
        learning_rate = 0.01  # learning rate for step: weight -= lr * step
        w = 0.01  # initial weight
        b = 0.0  # here unbiased data is considered so b = 0
        # epochs' loop: 5000 epochs
        for i in range(iterations):
            z = w * X + b
            val = -self.np.multiply(y, z)
            num = -self.np.multiply(y, self.np.exp(val))
            den = 1 + self.np.exp(val)
            f = num / den  # f is gradient dJ for each data point
            gradJ = self.np.sum(X * f)  # total dJ
            w = w - learning_rate * gradJ / len(x)  # SAG subtraction
        # Accuracy calculation
        error = 0  # incorrect values
        for x_id in range(len(X)):
            yhat = X[x_id] * w + b > 0.5
            if yhat:
                yhat = 1
            else:
                yhat = 0
            if yhat != y[x_id]:
                error += 1
        accuracy = 1 - (error / len(x))
        return (w, b, accuracy)

    async def train(self, sources: Sources):
        async for record in sources.with_features(
            self.features + [self.config.predict.name]
        ):
            feature_data = record.features(
                self.features + [self.config.predict.name]
            )
            self.X = self.np.append(
                self.X, feature_data[self.features[0]]
            )
            self.y = self.np.append(
                self.y, feature_data[self.config.predict.name]
            )
        self.separating_line = self.best_separating_line()

    async def accuracy(self, sources: Sources) -> Accuracy:
        # Ensure the model has been trained before we try to make a prediction
        if self.separating_line is None:
            raise ModelNotTrained("Train model before assessing for accuracy.")
        accuracy_value = self.separating_line[2]
        return Accuracy(accuracy_value)

    async def predict(
        self, sources: SourcesContext
    ) -> AsyncIterator[Tuple[Record, Any, float]]:
        # Ensure the model has been trained before we try to make a prediction
        if self.separating_line is None:
            raise ModelNotTrained("Train model before prediction.")
        target = self.config.predict.name
        async for record in sources.with_features(
            self.parent.config.features.names()
        ):
            feature_data = record.features(self.features)
            record.predicted(
                target,
                self.predict_input(feature_data[self.features[0]]),
                self.separating_line[2],
            )
            yield record
