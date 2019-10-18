"""
Uses Tensorflow to create a generic DNN which learns on all of the features in a
repo.
"""
import os
import abc
import pydoc
import hashlib
import inspect
from dataclasses import dataclass
from typing import List, Dict, Any, AsyncIterator, Tuple, Optional, Type

import numpy as np
import tensorflow

from dffml.repo import Repo
from dffml.feature import Feature, Features
from dffml.source.source import Sources
from dffml.model.model import ModelConfig, ModelContext, Model
from dffml.accuracy import Accuracy
from dffml.util.entrypoint import entry_point
from dffml.base import BaseConfig
from dffml.util.cli.arg import Arg

from dffml_model_tensorflow.dnnc import TensorflowModelContext

DEBUG =True
@dataclass(init=True, eq=True)
class DNNRegressionModelConfig:
    directory: str
    steps: int
    epochs: int
    hidden: List[int]
    label_name : str # feature_name holding target values 
    
    

class DNNRegressionModelContext(TensorflowModelContext):
    """
    Model using tensorflow to make predictions. Handels creation of feature
    columns for real valued, string, and list of real valued features.
    """

    def __init__(self, config, parent) -> None:
        super().__init__(config, parent)
        self.model_dir_path = self._model_dir_path()
        self.label_name=self.parent.config.label_name
        self.all_features=self.features+[self.label_name]
  
    def _model_dir_path(self):
        """
        Creates the path to the model dir by using the provided model dir and
        the sha384 hash of the concatenated feature names.
        """
        if self.parent.config.directory is None:
            return None
        _to_hash = self.features + list(map(str, self.parent.config.hidden))
        model = hashlib.sha384("".join(_to_hash).encode("utf-8")).hexdigest()
        if not os.path.isdir(self.parent.config.directory):
            raise NotADirectoryError(
                "%s is not a directory" % (self.parent.config.directory)
            )
        return os.path.join(self.parent.config.directory, model)

    @property
    def model(self):
        """
        Generates or loads a model
        """
        if self._model is not None:
            return self._model
        self.logger.debug(
            "Loading model ")
      
        _head=tensorflow.contrib.estimator.regression_head()
        self._model = tensorflow.estimator.DNNEstimator(
                head=_head,
                feature_columns=list(self.feature_columns.values()),
                hidden_units=self.parent.config.hidden,
                model_dir=self.model_dir_path,
              )
        
        return self._model

    async def training_input_fn(self,sources: Sources,batch_size=20,shuffle=False,epochs=1,**kwargs,):
        """
        Uses the numpy input function with data from repo features.
        """
        self.logger.debug("Training on features: %r", self.features)
        x_cols: Dict[str, Any] = {feature: [] for feature in self.features}
        y_cols = []
        
        async for repo in sources.with_features(self.all_features ):
            for feature, results in repo.features(self.features).items():
                
                x_cols[feature].append(np.array(results))
            y_cols.append(repo.feature(self.label_name))

        y_cols = np.array(y_cols)
        for feature in x_cols:
            x_cols[feature] = np.array(x_cols[feature])
        self.logger.info("------ Repo Data ------")
        self.logger.info("x_cols:    %d", len(list(x_cols.values())[0]))
        self.logger.info("y_cols:    %d", len(y_cols))
        self.logger.info("-----------------------")
        input_fn = tensorflow.estimator.inputs.numpy_input_fn(
            x_cols,
            y_cols,
            batch_size=batch_size,
            shuffle=shuffle,
            num_epochs=epochs,
            **kwargs,
        )
        return input_fn

    async def evaluate_input_fn(self,sources: Sources,batch_size=20,shuffle=False,epochs=1,**kwargs,):
        """
        Uses the numpy input function with data from repo features.
        """
        x_cols: Dict[str, Any] = {feature: [] for feature in self.features}
        y_cols = []

        async for repo in sources.with_features(self.all_features ):
            for feature, results in repo.features(self.features).items():
                x_cols[feature].append(np.array(results))
            y_cols.append(repo.feature(self.label_name))

        y_cols = np.array(y_cols)
        for feature in x_cols:
            x_cols[feature] = np.array(x_cols[feature])
        self.logger.info("------ Repo Data ------")
        self.logger.info("x_cols:    %d", len(list(x_cols.values())[0]))
        self.logger.info("y_cols:    %d", len(y_cols))
        self.logger.info("-----------------------")
        input_fn = tensorflow.estimator.inputs.numpy_input_fn(
            x_cols,
            y_cols,
            batch_size=batch_size,
            shuffle=shuffle,
            num_epochs=epochs,
            **kwargs,
        )
        return input_fn

    async def predict_input_fn(self, repos: AsyncIterator[Repo], **kwargs):
        """
        Uses the numpy input function with data from repo features.
        """
        x_cols: Dict[str, Any] = {feature: [] for feature in self.features}
        ret_repos = []
        async for repo in repos:
            if not repo.features(self.features):
                continue
            ret_repos.append(repo)
            for feature, results in repo.features(self.features).items():
                x_cols[feature].append(np.array(results))
        for feature in x_cols:
            x_cols[feature] = np.array(x_cols[feature])
        self.logger.info("------ Repo Data ------")
        self.logger.info("x_cols:    %d", len(list(x_cols.values())[0]))
        self.logger.info("-----------------------")
        input_fn = tensorflow.estimator.inputs.numpy_input_fn(
            x_cols, shuffle=False, num_epochs=1, **kwargs
        )
        return input_fn, ret_repos

    async def train(self, sources: Sources):
        """
        Train on data submitted via classify.
        """
        input_fn = await self.training_input_fn(
            sources,
            batch_size=20,
            shuffle=True,
            epochs=self.parent.config.epochs,
        )
        self.model.train(input_fn=input_fn, steps=self.parent.config.steps)

    async def accuracy(self, sources: Sources) -> Accuracy:
        """
        Evaluates the accuracy of our model after training using the input repos
        as test data.
        """
        if not os.path.isdir(self.model_dir_path):
            raise NotADirectoryError("Model not trained")
        input_fn = await self.evaluate_input_fn(
            sources, batch_size=20, shuffle=False, epochs=1
        )
        metrics = self.model.evaluate(input_fn=input_fn)
        return Accuracy(1-metrics["loss"]) # 1 - mse

    async def predict(self, repos: AsyncIterator[Repo]) -> AsyncIterator[Repo]:
        """
        Uses trained data to make a prediction about the quality of a repo.
        """
        
        if not os.path.isdir(self.model_dir_path):
            raise NotADirectoryError("Model not trained")
        # Create the input function
        input_fn, predict_repo = await self.predict_input_fn(repos)
        # Makes predictions on 
        predictions = self.model.predict(input_fn=input_fn)
   
        for repo, pred_dict in zip(predict_repo, predictions):
            repo.predicted(float(pred_dict["predictions"]),float('nan')) # 0,arbitary number to match fun signature -> (value,confidence)
           
            yield repo


@entry_point("tfdnnr")
class DNNRegressionModel(Model):
   

    CONTEXT = DNNRegressionModelContext

    @classmethod
    def args(cls, args, *above) -> Dict[str, Arg]:
        cls.config_set(
            args,
            above,
            "directory",
            Arg(
                default=os.path.join(
                    os.path.expanduser("~"), ".cache", "dffml", "tensorflow"
                ),
                help="Directory where state should be saved",
            ),
        )
        cls.config_set(
            args,
            above,
            "steps",
            Arg(
                type=int,
                default=3000,
                help="Number of steps to train the model",
            ),
        )
        cls.config_set(
            args,
            above,
            "epochs",
            Arg(
                type=int,
                default=30,
                help="Number of iterations to pass over all repos in a source",
            ),
        )
        cls.config_set(
            args,
            above,
            "hidden",
            Arg(
                type=int,
                nargs="+",
                default=[12, 40, 15],
                help="List length is the number of hidden layers in the network. Each entry in the list is the number of nodes in that hidden layer",
            ),
        )
        cls.config_set(
            args,
            above,
            "label_name",
            Arg(help="Feature name holding truth value"),
        )
       
        return args

    @classmethod
    def config(cls, config, *above) -> BaseConfig:
        return DNNRegressionModelConfig(
            directory=cls.config_get(config, above, "directory"),
            steps=cls.config_get(config, above, "steps"),
            epochs=cls.config_get(config, above, "epochs"),
            hidden=cls.config_get(config, above, "hidden"),
            label_name=cls.config_get(config, above, "label_name"),
           
        )
