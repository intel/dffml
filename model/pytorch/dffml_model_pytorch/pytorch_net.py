import operator
import torch.nn as nn

from dffml.base import config, field
from dffml.util.entrypoint import entrypoint
from dffml.model.model import Model
from .pytorch_base import PyTorchModelConfig, PyTorchModelContext
from .utils import create_layer


class Network(nn.Module):
    def __init__(self, network):
        super(Network, self).__init__()
        if isinstance(network, dict):
            self.setUp(network)
        elif isinstance(network, nn.Module):
            return network
        else:
            raise ValueError(
                "network should be a dict or a Pytorch Model(nn.Module)"
            )

    def forward(self, x):
        for model in self.feedforward:
            for layer in self.feedforward[model]:
                if isinstance(layer, dict) and "view" in layer.keys():
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
            layer = create_layer(value)
            self.add_module(key, layer)


@config
class PyTorchNeuralNetworkConfig(PyTorchModelConfig):
    network: Network = field("Model", default=None)


class PyTorchNeuralNetworkContext(PyTorchModelContext):
    def __init__(self, parent):
        super().__init__(parent)

    def createModel(self):
        """
        Generates a model
        """
        if self._model is not None:
            return self._model

        if self.classifications:
            self.logger.debug(
                "Loading model with classifications(%d): %r",
                len(self.classifications),
                self.classifications,
            )

        model = self.parent.config.network
        self.logger.debug("Model Summary\n%r", model)

        self._model = model.to(self.device)
        return self._model


@entrypoint("pytorchnet")
class PyTorchNeuralNetwork(Model):
    CONFIG = PyTorchNeuralNetworkConfig
    CONTEXT = PyTorchNeuralNetworkContext
