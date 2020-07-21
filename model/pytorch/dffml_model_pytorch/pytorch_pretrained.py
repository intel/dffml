from __future__ import print_function, division

import torch.nn as nn
import torch.optim as optim
from torch.optim import lr_scheduler
from torchvision import models

from dffml.util.entrypoint import entrypoint
from dffml.base import config
from dffml.model.model import Model
from .pytorch_base import PyTorchModelConfig, PyTorchModelContext


@config
class ResNet18ModelConfig(PyTorchModelConfig):
    pass


class ResNet18ModelContext(PyTorchModelContext):
    def __init__(self, parent):
        super().__init__(parent)

    def createModel(self):
        """
        Generates a model
        """
        if self._model is not None:
            return self._model
        self.logger.debug(
            "Loading model with classifications(%d): %r",
            len(self.classifications),
            self.classifications,
        )

        model = models.resnet18(pretrained=True)
        for param in model.parameters():
            param.require_grad = self.parent.config.trainable

        model.fc = nn.Sequential(
            nn.Linear(model.fc.in_features, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, len(self.classifications)),
            nn.LogSoftmax(dim=1),
        )
        self._model = model.to(self.device)

        # Metrics
        self.criterion = nn.CrossEntropyLoss()
        model_parameters = (
            self._model.parameters()
            if self.parent.config.trainable
            else self._model.fc.parameters()
        )
        self.optimizer = optim.SGD(model_parameters, lr=0.001, momentum=0.9)
        self.exp_lr_scheduler = lr_scheduler.StepLR(
            self.optimizer, step_size=7, gamma=0.1
        )

        return self._model


@entrypoint("resnet18")
class ResNet18Model(Model):

    CONFIG = ResNet18ModelConfig
    CONTEXT = ResNet18ModelContext


@config
class VGG16ModelConfig(PyTorchModelConfig):
    pass


class VGG16ModelContext(PyTorchModelContext):
    def __init__(self, parent):
        super().__init__(parent)

    def createModel(self):
        """
        Generates a model
        """
        if self._model is not None:
            return self._model
        self.logger.debug(
            "Loading model with classifications(%d): %r",
            len(self.classifications),
            self.classifications,
        )

        model = models.vgg16(pretrained=True)
        for param in model.parameters():
            param.require_grad = self.parent.config.trainable

        num_features = model.classifier[-1].in_features
        features = list(model.classifier.children())[:-1]
        features.append(
            nn.Sequential(
                nn.Linear(num_features, 256),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(256, len(self.classifications)),
                nn.LogSoftmax(dim=1),
            )
        )
        model.classifier = nn.Sequential(*features)
        self._model = model.to(self.device)

        # Metrics
        self.criterion = nn.CrossEntropyLoss()
        model_parameters = (
            self._model.classifier.parameters()
            if self.parent.config.trainable
            else self._model.classifier[-1].parameters()
        )
        self.optimizer = optim.SGD(model_parameters, lr=0.001, momentum=0.9)
        self.exp_lr_scheduler = lr_scheduler.StepLR(
            self.optimizer, step_size=7, gamma=0.1
        )

        return self._model


@entrypoint("vgg16")
class VGG16Model(Model):

    CONFIG = VGG16ModelConfig
    CONTEXT = VGG16ModelContext
