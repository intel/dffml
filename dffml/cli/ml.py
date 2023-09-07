import inspect

from ..model.model import Model
from ..tuner.tuner import Tuner
from ..source.source import Sources, SubsetSources
from ..util.cli.cmd import CMD, CMDOutputOverride
from ..high_level.ml import train, predict, score, tune
from ..util.config.fields import FIELD_SOURCES
from ..util.cli.cmds import (
    SourcesCMD,
    ModelCMD,
    KeysCMD,
    ModelCMDConfig,
    SourcesCMDConfig,
    KeysCMDConfig,
)
from ..base import config, field
from ..accuracy import AccuracyScorer

from ..feature import Features


@config
class MLCMDConfig(SourcesCMDConfig, ModelCMDConfig):
    pass


@config
class AccuracyCMDConfig:
    model: Model = field("Model used for ML", required=True)
    scorer: AccuracyScorer = field(
        "Method to use to score accuracy", required=True
    )
    features: Features = field("Predict Feature(s)", default=Features())
    sources: Sources = FIELD_SOURCES


class MLCMD(SourcesCMD, ModelCMD):
    """
    Commands which use models share many similar arguments.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ModelCMD.__init__(self, *args, **kwargs)


class Train(MLCMD):
    """Train a model on data from given sources"""

    """
    changes : model(features) -> model()
    """

    CONFIG = MLCMDConfig

    async def run(self):
        return await train(self.model, self.sources)


class Accuracy(MLCMD):
    """Assess model accuracy on data from given sources"""

    CONFIG = AccuracyCMDConfig

    async def run(self):
        # Instantiate the accuracy scorer class if for some reason it is a class
        # at this point rather than an instance.
        if inspect.isclass(self.scorer):
            self.scorer = self.scorer.withconfig(self.extra_config)
        return await score(
            self.model, self.scorer, self.features, self.sources
        )


@config
class PredictAllConfig(MLCMDConfig):
    update: bool = field(
        "Update record with sources", default=False,
    )
    pretty: bool = field(
        "Outputs data in tabular form", default=False,
    )


class PredictAll(MLCMD):
    """Predicts for all sources"""

    CONFIG = PredictAllConfig

    async def run(self):
        async for record in predict(
            self.model, self.sources, update=self.update, keep_record=True
        ):
            if self.pretty:
                print(record)
            else:
                yield record
        if self.pretty:
            yield CMDOutputOverride


@config
class PredictRecordConfig(PredictAllConfig, KeysCMDConfig):
    pass


class PredictRecord(PredictAll, KeysCMD):
    """Predictions for individual records"""

    CONFIG = PredictRecordConfig

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sources = SubsetSources(*self.sources, keys=self.keys)


class Predict(CMD):
    """Evaluate features against records and produce a prediction"""

    record = PredictRecord
    _all = PredictAll


@config
class TuneCMDConfig:
    model: Model = field("Model used for ML", required=True)
    tuner: Tuner = field("Tuner to optimize hyperparameters", required=True)
    scorer: AccuracyScorer = field(
        "Method to use to score accuracy", required=True
    )
    features: Features = field("Predict Feature(s)", default=Features())
    sources: Sources = FIELD_SOURCES
  

class Tune(MLCMD):
    """Optimize hyperparameters of model with given sources"""

    CONFIG = TuneCMDConfig

    async def run(self):
        # Instantiate the accuracy scorer class if for some reason it is a class
        # at this point rather than an instance.
        if inspect.isclass(self.scorer):
            self.scorer = self.scorer.withconfig(self.extra_config)
        if inspect.isclass(self.tuner):
            self.tuner = self.tuner.withconfig(self.extra_config)
        
        train_source = test_source = None
        
        # Check for tags to determine train/test sets 
        for source in self.sources:
        
            if hasattr(source, "tag") and source.tag == "train":
                train_source = source
            if hasattr(source, "tag") and source.tag == "test":
                test_source = source
    
        if not train_source or not test_source:
            # If tags not found, default to positional
            if len(self.sources) >= 2:
                train_source = self.sources[0]
                test_source = self.sources[1]
            elif not train_source:
                raise NotImplementedError("Train set not found.")
            else:
                raise NotImplementedError("Test set not found.")
        
        return await tune(
            self.model,
            self.tuner,
            self.scorer,
            self.features,
            [train_source],
            [test_source],
        )
