"""
Uses Tensorflow to create a generic DNN which learns on all of the features in a
repo.
"""
import os
import hashlib
from dataclasses import dataclass
from typing import List, Dict, Any, AsyncIterator

import numpy as np
import tensorflow

from dffml.repo import Repo
from dffml.source.source import Sources
from dffml.model.model import  Model
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
    predict : str # feature_name holding target values 
    
    

class DNNRegressionModelContext(TensorflowModelContext):
    """
    Model using tensorflow to make predictions. Handels creation of feature
    columns for real valued, string, and list of real valued features.
    """

    def __init__(self, config, parent) -> None:
        super().__init__(config, parent)
        self.model_dir_path = self._model_dir_path()
        self.all_features=self.features+[self.parent.config.predict]
  
    

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
            y_cols.append(repo.feature(self.parent.config.predict))

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
            y_cols.append(repo.feature(self.parent.config.predict))

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
    """
    Implemented using Tensorflow's DNNEstimator. Models are saved under the
    ``directory`` in subdirectories named after the hash of their feature names and hidden layer config.

    usage :
        * predict : column_name of target
        * NOTE : if multiple models are trained then `model-hidden` should be passed to hash to the
                    model directory

    dffml train \
          -model tfdnnr \
          -model-epochs 300 \
          -model-steps 2000 \
          -model-predict {$TARGET_COLUMN_NAME} \
          -model-hidden 12 40 50 \
          -sources s=csv \
          -source-readonly \
          -source-filename {$TRAIN_DATA_FILENAME}.csv \
          -features \
            def:{$feature1}:float:1 \
            def:{$feature2}:float:1 \
            def:{$feature3}:float:1 \
          -log debug
    
     dffml accuracy \
          -model tfdnnr \
          -model-predict {$TARGET_COLUMN_NAME} \
          -model-hidden 12 40 50 \
          -sources s=csv \
          -source-readonly \
          -source-filename {$TRAIN_DATA_FILENAME}.csv \
          -features \
            def:{$feature1}:float:1 \
            def:{$feature2}:float:1 \
            def:{$feature3}:float:1 \
          -log debug
    
    dffml predict all \
          -model tfdnnr \
          -model-predict {$TARGET_COLUMN_NAME} \
          -model-hidden 12 40 50 \
          -sources s=csv \
          -source-readonly \
          -source-filename {$TEST_DATA_FILENAME}.csv \
          -features \
            def:{$feature1}:float:1 \
            def:{$feature2}:float:1 \
            def:{$feature3}:float:1 \
          -log debug
   """

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
            "predict",
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
            predict=cls.config_get(config, above, "predict"),
           
        )
