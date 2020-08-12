import logging
import operator
import sys
import pathlib
from typing import Any, List, Type
import torch.nn as nn
from torchvision import models

from dffml.base import config, field
from dffml.feature.feature import Feature, Features
from dffml.util.entrypoint import entrypoint
from dffml.model.model import Model
from dffml.configloader.configloader import BaseConfigLoader
from .pytorch_base import PyTorchModelConfig, PyTorchModelContext


class Net(nn.Module):
    def __init__(self, network):
        super(Net, self).__init__()
        self.setUp(network)

    def forward(self, x):
        for layer in self.model:
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

        if "forward" in network.keys():
            self.model = network["forward"]
        else:
            for model in self.models.keys():
                self.model = list(network[model].keys())

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
    network: pathlib.Path = field("Model")
    classifications: List[str] = field("Options for value of classification")
    predict: Feature = field("Feature name holding classification value")
    features: Features = field("Features to train on")
    directory: pathlib.Path = field("Directory where state should be saved")
    configloader: BaseConfigLoader = field("ConfigLoader", default=None)
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

    async def __aenter__(self):

        if isinstance(self.parent.config.network, (str, pathlib.PosixPath,)):
            network_path = pathlib.Path(self.parent.config.network)
            config_cls = self.parent.config.configloader
            if config_cls is None:
                config_type = network_path.suffix.replace(".", "")
                config_cls = BaseConfigLoader.load(config_type)
            # config_cls = BaseConfigLoader.load(self.parent.config.configloader)

            async with config_cls.withconfig({}) as configloader:
                async with configloader() as loader:
                    exported = await loader.loadb(network_path.read_bytes())
                self.parent.config.network = Net(exported)

        await super().__aenter__()
        return self

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


@entrypoint("pytorch_nn")
class PyTorchNeuralNetwork(Model):
    CONFIG = PyTorchNeuralNetworkConfig
    CONTEXT = PyTorchNeuralNetworkContext
    LAST_LAYER_TYPE = None
