import logging
import operator
import sys
import pathlib
from typing import Any, List, Type, Dict
import torch.nn as nn
from torchvision import models

from dffml.base import config, field
from dffml.feature.feature import Feature, Features
from dffml.util.entrypoint import entrypoint
from dffml.model.model import Model
from .pytorch_base import PyTorchModelConfig, PyTorchModelContext


class Network(nn.Module):
    def __init__(self, network):
        super(Network, self).__init__()
        if isinstance(network, dict):
            self.setUp(network)
        elif isinstance(network, nn.Module):
            return network
        else:
            raise ValueError("network should be a dict or a Pytorch Model")

    def forward(self, x):
        for model in self.feedforward:
            for layer in self.feedforward[model]:
                if isinstance(layer, dict) and "view" in layer.keys():
                    # TODO Add more custom functions (not part of nn Module) if you find it
                    x = x.view(*layer["view"])
                    continue
                x = operator.attrgetter(layer)(self)(x)
        return x

    def setUp(self, network):
        self.models = {
            key: value
            for key, value in network.items()
            if not key.lower() == "forward"
        }
        for model in self.models.keys():
            self.add_layers(self.models[model])

        self.feedforward = {}
        if "forward" in network.keys():
            for model in self.models.keys():
                self.feedforward[model] = network["forward"][model]
        else:
            for model in self.models.keys():
                self.feedforward[model] = list(network[model].keys())

    def add_layers(self, data):
        for key, value in data.items():
            try:
                sequential_dict = nn.Sequential()
                for name, layer in value.items():
                    parameters = {k: v for k, v in layer.items()}
                    layer_name = parameters.pop("name")

                    sequential_dict.add_module(
                        name, getattr(nn, layer_name)(**parameters)
                    )
                self.add_module(key, sequential_dict)
            except AttributeError:
                parameters = {k: v for k, v in value.items()}
                layer_name = parameters.pop("name")
                self.add_module(key, getattr(nn, layer_name)(**parameters))


@config
class PyTorchNeuralNetworkConfig:
    classifications: List[str] = field("Options for value of classification")
    predict: Feature = field("Feature name holding classification value")
    features: Features = field("Features to train on")
    directory: pathlib.Path = field("Directory where state should be saved")
    network: Network = field("Model")
    clstype: Type = field("Data type of classifications values", default=str)
    imageSize: int = field(
        "Common size for all images to resize and crop to", default=224
    )
    enableGPU: bool = field("Utilize GPUs for processing", default=False)
    epochs: int = field(
        "Number of iterations to pass over all records in a source", default=20
    )
    trainable: bool = field(
        "Tweak pretrained model by training again", default=False
    )
    batch_size: int = field("Batch size", default=32)
    validation_split: float = field(
        "Split training data for Validation", default=0.0
    )
    patience: int = field(
        "Early stops the training if validation loss doesn't improve after a given patience",
        default=5,
    )


class PyTorchNeuralNetworkContext(PyTorchModelContext):
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

        model = self.parent.config.network
        self.logger.debug("Model Summary\n%r", model)
        for param in model.parameters():
            param.require_grad = self.parent.config.trainable

        self._model = model.to(self.device)
        return self._model


@entrypoint("pytorchnn")
class PyTorchNeuralNetwork(Model):
    CONFIG = PyTorchNeuralNetworkConfig
    CONTEXT = PyTorchNeuralNetworkContext
    LAST_LAYER_TYPE = None
