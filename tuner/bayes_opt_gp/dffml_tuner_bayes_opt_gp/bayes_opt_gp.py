from typing import Union, Dict, Any, List
import itertools
import logging

from dffml.base import (
    config,
    field,
)
from dffml.noasync import train, score
from dffml.tuner import Tuner, TunerContext
from dffml.util.entrypoint import entrypoint
from dffml.record import Record
from dffml.source.source import BaseSource
from dffml.accuracy import AccuracyScorer, AccuracyContext
from dffml.model import ModelContext
from dffml.feature import Feature
import nest_asyncio
from bayes_opt import BayesianOptimization


class InvalidParametersException(Exception):
    pass


@config
class BayesOptGPConfig:
    parameters: dict = field(
        "Parameters to be optimized", default_factory=lambda: dict()
    )
    objective: str = field(
        "How to optimize the given scorer. Values are min/max", default="max"
    )
    init_points: int = field(
        "How many steps of random exploration you want to perform.", default=5
    )
    n_iter: int = field(
        "How many steps of bayesian optimization you want to perform.",
        default=10,
    )


class BayesOptGPContext(TunerContext):
    """
    Bayesian Optimization GP Tuner
    """

    async def optimize(
        self,
        model: ModelContext,
        feature: Feature,
        accuracy_scorer: Union[AccuracyScorer, AccuracyContext],
        train_data: Union[BaseSource, Record, Dict[str, Any]],
        test_data: Union[BaseSource, Record, Dict[str, Any]],
    ):
        """
        Method to optimize hyperparameters by Bayesian optimization using Gaussian Processes
        as the surrogate model.
        Uses a grid of hyperparameters in the form of a dictionary present in config,
        Trains each permutation of the grid of parameters and compares accuracy.
        Sets model to the best parameters and returns highest accuracy.

        Note that for this tuner, each hyperparameter field to be tuned must have exactly 2 values 
        specified, representing the minimum and maximum values in the search space for that 
        hyperparameter. Additionally, they must be either float/integer values. Otherwise,
        an error is raised.

        Parameters
        ----------
        model : ModelContext
            The Model which needs to be used.

        feature : Feature
            The Target feature in the data.

        accuracy_scorer: AccuracyContext
            The accuracy scorer that needs to be used.

        train_data: SourcesContext
            The train_data to train models on with the hyperparameters provided.

        sources : SourcesContext
            The test_data to score against and optimize hyperparameters.

        Returns
        -------
        float
            The highest score value
        """

        nest_asyncio.apply()

        def check_parameters(pars):
            for (pax, vals) in pars.items():
                if len(vals) != 2:
                    raise InvalidParametersException(
                        f"2 values are not provided for parameter {pax}"
                    )
                for val in vals:
                    if not type(val) is float and not type(val) is int:
                        raise InvalidParametersException(
                            f"Parameter {pax} is not of type int or float."
                        )
            return True

        check_parameters(self.parent.config.parameters)

        logging.info(
            f"Optimizing model with Bayesian optimization with gaussian processes: {self.parent.config.parameters}"
        )

        def func(**vals):
            with model.parent.config.no_enforce_immutable():
                for param in vals.keys():

                    if (
                        hasattr(model.parent.config, param)
                        and model.parent.config.__annotations__[param].__name__
                        == "int"
                    ):
                        setattr(model.parent.config, param, int(vals[param]))
                    else:
                        setattr(model.parent.config, param, vals[param])

                train(model.parent, *train_data)
                acc = score(model.parent, accuracy_scorer, feature, *test_data)

                if self.parent.config.objective == "min":
                    return -acc
                elif self.parent.config.objective == "max":
                    return acc

        optimizer = BayesianOptimization(
            f=func,
            pbounds=self.parent.config.parameters,
            random_state=1,
        )

        optimizer.maximize(
            init_points=self.parent.config.init_points,
            n_iter=self.parent.config.n_iter,
        )
        with model.parent.config.no_enforce_immutable():
            for (param, val) in optimizer.max["params"].items():

                if (
                    hasattr(model.parent.config, param)
                    and model.parent.config.__annotations__[param].__name__
                    == "int"
                ):
                    setattr(model.parent.config, param, int(val))
                else:
                    setattr(model.parent.config, param, val)

            train(model.parent, *train_data)

        if self.parent.config.objective == "min":
            return -optimizer.max["target"]
        elif self.parent.config.objective == "max":
            return optimizer.max["target"]


@entrypoint("bayes_opt_gp")
class BayesOptGP(Tuner):

    CONFIG = BayesOptGPConfig
    CONTEXT = BayesOptGPContext
