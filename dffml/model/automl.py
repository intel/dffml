import pathlib
import os
import shutil
import tempfile
import contextlib
import pkg_resources
from typing import AsyncIterator, Tuple, Any, Type, List
from ..high_level.ml import tune
from ..base import config, field
from ..util.entrypoint import entrypoint
from .model import ModelNotTrained, ModelContext, SimpleModel, Model
from ..feature.feature import Feature, Features
from ..source.source import Sources, SourcesContext
from ..record import Record
from ..model.model import Model
from ..tuner.tuner import Tuner
from ..accuracy import AccuracyScorer


@config
class AutoMLModelConfig:
    predict: Feature = field("Label or the value to be predicted")
    features: Features = field("Features to train on.")
    location: pathlib.Path = field("Location where state should be saved")
    tuner: Tuner = field("Tuner to optimize hyperparameters with.")
    scorer: AccuracyScorer = field("Scorer to evaluate and select best model.")
    models: List[str] = field("List of models to tune and compare against", default_factory= lambda:list())
    objective: str = field(
        "How to optimize the given scorer. Values are min/max", default="max"
    )


@entrypoint("automl")
class AutoMLModel(SimpleModel):
    r"""
    AutoML model for automatic training and tuning based on target datasets and given
    models and tuner.

    """
    # The configuration class needs to be set as the CONFIG property
    
    CONFIG: Type[AutoMLModelConfig] = AutoMLModelConfig

    def __init__(self, config) -> None:
        super().__init__(config)
        # The saved model
        self.saved = None

    async def __aenter__(self):
        await super().__aenter__()


        dest = pathlib.Path(self.parent.config.location)
        best_path = dest / "best_model"
        # Check if model has been trained, and if so, get the type of the model
        best_model = best_model_path =  None
        if dest.exists() and best_path.exists() and len(os.listdir(best_path)):
            best_model = os.listdir(best_path)[0]
     
        # We want to allow users to not need to deal with individual model configuration. 
        # So we accept a list of strings and initialize our models based on that.
        self.model_classes = {}
        for ep in pkg_resources.iter_entry_points(group='dffml.model'):
            if ep.name in self.parent.config.models or ep.name == best_model:
                self.model_classes.update({ep.name: ep.load()})
        

        if best_model:
            model = self.model_classes[best_model](
                location = best_path / best_model,
                features = self.parent.config.features,
                predict = self.parent.config.predict
            )
            async with contextlib.AsyncExitStack() as astack:
                if isinstance(model, Model):
                    model = await astack.enter_async_context(model)
                    mctx = await astack.enter_async_context(model())
                elif isinstance(model, ModelContext):
                    mctx = model
            self.saved = mctx
            self.is_trained = True
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await super().__aexit__(exc_type, exc_value, traceback)

    async def train(self, sources: Sources) -> None:

        tuner = self.parent.config.tuner
        scorer = self.parent.config.scorer
        features = self.parent.config.features
        location = self.parent.config.location
        source_files = sources[0]

        tuner.config.objective = self.parent.config.objective 
            
        train_source = test_source = None

        
        # Check for tags to determine train/test sets 
        for source in source_files:
        
            if hasattr(source, "tag") and source.tag == "train":
                train_source = source
            if hasattr(source, "tag") and source.tag == "test":
                test_source = source
    
        if not train_source or not test_source:
            # If tags not found, default to positional
            if len(source_files) >= 2:
                train_source = source_files[0]
                test_source = source_files[1]
            elif not train_source:
                raise NotImplementedError("Train set not found.")
            else:
                raise NotImplementedError("Test set not found.")

        if self.parent.config.objective == "min":
            highest_acc = float("inf")
        elif self.parent.config.objective == "max":
            highest_acc = -1
        else:
            raise NotImplementedError('Objective must be either "min" or "max".')

        dest = pathlib.Path(location)
        # We clear the destination directory first, to avoid conflicts.
        if dest.exists() and dest.is_dir():
            shutil.rmtree(dest)
  

        best_path = best_name = ""

        for model_name in self.parent.config.models:
            model_dir = dest / model_name
   
            model = self.model_classes[model_name](
                location = model_dir,
                features = features,
                predict = self.parent.config.predict
            )
      
            val = await tune(model, tuner, scorer, self.parent.config.predict, [train_source], [test_source])
            if self.parent.config.objective == "min" and val < highest_acc:
                best_path = model_dir
                best_name = model_name
            elif self.parent.config.objective == "max" and val > highest_acc:
                best_path = model_dir
                best_name = model_name
        
        best_model_dir = dest / "best_model" / best_name
        shutil.copytree(best_path, best_model_dir)

      

    async def predict(
        self, sources: SourcesContext
    ) -> AsyncIterator[Tuple[Record, Any, float]]:
        if not self.is_trained:
            raise ModelNotTrained(
                "Train the model first before getting predictions"
            )
        # Use the child model API to make predictions
        async for record in self.saved.predict(sources):
            yield record
