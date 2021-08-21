import torch

from dffml.base import config
from dffml.source.source import Sources
from dffml.feature.feature import Features
from dffml.util.entrypoint import entrypoint
from dffml.model import ModelNotTrained, ModelContext
from dffml.accuracy import (
    AccuracyScorer,
    AccuracyContext,
)


@config
class PytorchAccuracyConfig:
    pass


class PytorchAccuracyContext(AccuracyContext):
    """
    Accuracy Scorer for Pytorch Network Models
    """

    async def score(
        self, mctx: ModelContext, sctx: Sources, *features: Features
    ):
        if not mctx.parent.model_path.exists():
            raise ModelNotTrained("Train model before assessing for accuracy.")

        dataset, size = await mctx.dataset_generator(sctx)
        dataloader = torch.utils.data.DataLoader(
            dataset,
            batch_size=mctx.parent.config.batch_size,
            shuffle=True,
            num_workers=4,
        )

        mctx.parent.model.eval()

        if mctx.parent.classifications:
            running_corrects = 0

            for inputs, labels in dataloader:
                inputs = inputs.to(mctx.parent.device)
                labels = labels.to(mctx.parent.device)

                with torch.set_grad_enabled(False):
                    outputs = mctx.parent.model(inputs)
                    _, preds = torch.max(outputs, 1)

                running_corrects += torch.sum(preds == labels.data)
                acc = running_corrects.double() / size
        else:
            running_loss = 0.0

            for inputs, labels in dataloader:
                inputs = inputs.to(inputs)
                labels = labels.to(inputs)

                with torch.set_grad_enabled(False):
                    outputs = mctx.parent.model(inputs)
                    loss = mctx.criterion(inputs, outputs)

                running_loss += loss.item() * inputs.size(0)

            total_loss = running_loss / size
            acc = 1.0 - total_loss

        return acc


@entrypoint("pytorchscore")
class PytorchAccuracy(AccuracyScorer):
    CONFIG = PytorchAccuracyConfig
    CONTEXT = PytorchAccuracyContext
