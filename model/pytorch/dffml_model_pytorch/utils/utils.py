import sys
import inspect

from torch import utils, nn
from torchvision import transforms

from dffml.base import BaseDataFlowFacilitatorObject
from dffml.util.entrypoint import base_entry_point, entrypoint
from .config import make_pytorch_config


def create_layer(layer_dict):
    try:
        sequential_dict = nn.Sequential()
        for name, layer in layer_dict.items():
            parameters = {k: v for k, v in layer.items()}
            layer_name = parameters.pop("name")

            sequential_dict.add_module(
                name, getattr(nn, layer_name)(**parameters)
            )
        return sequential_dict
    except AttributeError:
        parameters = {k: v for k, v in layer_dict.items()}
        layer_name = parameters.pop("name")
        return getattr(nn, layer_name)(**parameters)


class NumpyToTensor(utils.data.Dataset):
    def __init__(self, data, target=None, size=224):
        self.data = data
        self.target = target
        self.size = size

    def transform(self, data, size):
        return transforms.Compose(
            [
                transforms.ToPILImage(),
                transforms.Resize(size),
                transforms.CenterCrop((size, size)),
                transforms.ToTensor(),
                transforms.Normalize(
                    [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]
                ),
            ]
        )(data)

    def __getitem__(self, index):
        x = self.transform(self.data[index], self.size)

        if self.target is not None:
            y = self.target[index]
            return x, y
        else:
            return x

    def __len__(self):
        return len(self.data)


@base_entry_point("dffml.model.pytorch.loss", "loss")
class PyTorchLoss(BaseDataFlowFacilitatorObject):
    def __init__(self, config):
        super().__init__(config)
        self.function = self.LOSS(**self.config._asdict())

    @classmethod
    def load(cls, class_name: str = None):
        for name, loss_class in inspect.getmembers(nn, inspect.isclass):
            if name.endswith("Loss"):
                if name.lower() == class_name:
                    return eval(name + "Function")


for name, loss_class in inspect.getmembers(nn, inspect.isclass):
    if name.endswith("Loss"):

        cls_config = make_pytorch_config(name + "Config", loss_class)

        cls = entrypoint(name.lower())(
            type(
                name + "Function",
                (PyTorchLoss,),
                {"CONFIG": cls_config, "CONTEXT": {}, "LOSS": loss_class,},
            )
        )

        setattr(sys.modules[__name__], cls.__qualname__, cls)

# TODO Currently only the torch.nn module has annotations
# Add PyTorchOptimizer and PyTorchScheduler after the next torch release
# as they are currently adding type annotations for everything
