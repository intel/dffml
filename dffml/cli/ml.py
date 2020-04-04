from ..source.source import SubsetSources
from ..util.cli.arg import Arg
from ..util.cli.cmd import CMD
from ..high_level import train, predict, accuracy
from ..util.cli.cmds import SourcesCMD, ModelCMD, KeysCMD


class MLCMD(ModelCMD, SourcesCMD):
    """
    Commands which use models share many similar arguments.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        SourcesCMD.__init__(self, *args, **kwargs)


class Train(MLCMD):
    """Train a model on data from given sources"""

    """
    changes : model(features) -> model()
    """

    async def run(self):
        return await train(self.model, self.sources)


class Accuracy(MLCMD):
    """Assess model accuracy on data from given sources"""

    async def run(self):
        return await accuracy(self.model, self.sources)


class PredictAll(MLCMD):
    """Predicts for all sources"""

    arg_update = Arg(
        "-update",
        help="Update record with sources",
        required=False,
        default=False,
        action="store_true",
    )

    async def run(self):
        async for record in predict(
            self.model, self.sources, update=self.update, keep_record=True
        ):
            yield record


class PredictRecord(PredictAll, KeysCMD):
    """Predictions for individual records"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sources = SubsetSources(*self.sources, keys=self.keys)


class Predict(CMD):
    """Evaluate features against records and produce a prediction"""

    record = PredictRecord
    _all = PredictAll
