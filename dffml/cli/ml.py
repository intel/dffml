from ..source.source import SubsetSources
from ..util.cli.cmd import CMD, CMDOutputOverride
from ..high_level import train, predict, accuracy
from ..util.cli.cmds import (
    SourcesCMD,
    ModelCMD,
    KeysCMD,
    ModelCMDConfig,
    SourcesCMDConfig,
    KeysCMDConfig,
)
from ..base import config, field


@config
class MLCMDConfig(SourcesCMDConfig, ModelCMDConfig):
    pass


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

    CONFIG = MLCMDConfig

    async def run(self):
        return await accuracy(self.model, self.sources)


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
