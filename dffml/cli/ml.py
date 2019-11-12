from ..source.source import SubsetSources
from ..util.cli.arg import Arg
from ..util.cli.cmd import CMD
from ..util.cli.cmds import SourcesCMD, ModelCMD, KeysCMD


class MLCMD(ModelCMD, SourcesCMD):
    """
    Commands which use models share many similar arguments.
    """


class Train(MLCMD):
    """Train a model on data from given sources"""

    """
    changes : model(features) -> model()
    """

    async def run(self):
        async with self.sources as sources, self.model as model:
            async with sources() as sctx, model() as mctx:
                return await mctx.train(sctx)


class Accuracy(MLCMD):
    """Assess model accuracy on data from given sources"""

    async def run(self):
        async with self.sources as sources, self.model as model:
            async with sources() as sctx, model() as mctx:
                return float(await mctx.accuracy(sctx))


class PredictAll(MLCMD):
    """Predicts for all sources"""

    arg_update = Arg(
        "-update",
        help="Update repo with sources",
        required=False,
        default=False,
        action="store_true",
    )

    async def predict(self, mctx, sctx, repos):
        async for repo in mctx.predict(repos):
            yield repo
            if self.update:
                await sctx.update(repo)

    async def run(self):
        async with self.sources as sources, self.model as model:
            async with sources() as sctx, model() as mctx:
                async for repo in self.predict(mctx, sctx, sctx.repos()):
                    yield repo


class PredictRepo(PredictAll, KeysCMD):
    """Predictions for individual repos"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sources = SubsetSources(*self.sources, keys=self.keys)


class Predict(CMD):
    """Evaluate features against repos and produce a prediction"""

    repo = PredictRepo
    _all = PredictAll
