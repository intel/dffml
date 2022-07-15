from typing import Union, Dict, Any
import itertools
import logging
import random

from ..base import (
    config,
    field,
)
from ..high_level.ml import train, score
from .tuner import Tuner, TunerContext
from ..util.entrypoint import entrypoint
from ..source.source import BaseSource, Record
from ..accuracy.accuracy import AccuracyScorer, AccuracyContext
from ..model import ModelContext
from ..feature.feature import Feature


@config
class RandomSearchConfig:
    parameters: dict = field("Parameters to be optimized")
    objective: str = field(
        "How to optimize the given scorer. Values are min/max", default="max"
    )
    trials: int = field("Number of random configurations to try.", default=20)


class RandomSearchContext(TunerContext):
    """
    Parameter Grid Tuner
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
        Method to optimize hyperparameters by parameter grid.
        Uses a grid of hyperparameters in the form of a dictionary present in config,
        Trains each permutation of the grid of parameters and compares accuracy.
        Sets model to the best parameters and returns highest accuracy.

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

        test_data : SourcesContext
            The test_data to score against and optimize hyperparameters.

        Returns
        -------
        float
            The highest score value
        """

        if self.parent.config.objective == "min":
            highest_acc = float("inf")
        elif self.parent.config.objective == "max":
            highest_acc = -1
        else:
            raise NotImplementedError('Objective must be either "min" or "max".')

        best_config = dict()
        logging.info(
            f"Optimizing model with random search: {self.parent.config.parameters}"
        )

        names = list(self.parent.config.parameters.keys())
        logging.info(names)

        with model.parent.config.no_enforce_immutable():
            for _ in range(self.parent.config.trials):
                combination = []
                for pvs in self.parent.config.parameters.values():
                    combination.append(random.choice(pvs))
                logging.info(combination)

                for i in range(len(combination)):
                    param = names[i]
                    setattr(model.parent.config, names[i], combination[i])
                await train(model.parent, *train_data)
                acc = await score(
                    model.parent, accuracy_scorer, feature, *test_data
                )

                logging.info(f"Accuracy of the tuned model: {acc}")
                if self.parent.config.objective == "min":
                    if acc < highest_acc:
                        highest_acc = acc
                        for param in names:
                            best_config[param] = getattr(
                                model.parent.config, param
                            )
                elif self.parent.config.objective == "max":
                    if acc > highest_acc:
                        highest_acc = acc
                        for param in names:
                            best_config[param] = getattr(
                                model.parent.config, param
                            )
            for param in names:
                setattr(model.parent.config, param, best_config[param])
            await train(model.parent, *train_data)
        logging.info(f"\nOptimal Hyper-parameters: {best_config}")
        logging.info(f"Accuracy of Optimized model: {highest_acc}")
        return highest_acc


@entrypoint("random_search")
class RandomSearch(Tuner):

    CONFIG = RandomSearchConfig
    CONTEXT = RandomSearchContext
