import sys
import torch.nn as nn
from torchvision import models

from dffml.util.entrypoint import entrypoint
from dffml.model.model import Model
from dffml.base import config, field
from .pytorch_base import PyTorchModelConfig, PyTorchModelContext
from .utils import create_layer


class LayersNotFound(Exception):
    """
    Raised when add_layers is set to True but no layers are provided.
    """


@config
class PyTorchPreTrainedModelConfig(PyTorchModelConfig):
    pretrained: bool = field(
        "Load Pre-trained model weights", default=True,
    )
    trainable: bool = field(
        "Tweak pretrained model by training again", default=False
    )
    add_layers: bool = field(
        "Replace the last layer of the pretrained model", default=False,
    )
    layers: dict = field(
        "Extra layers to replace the last layer of the pretrained model",
        default=None,
    )


class PyTorchPretrainedContext(PyTorchModelContext):
    def __init__(self, parent):
        super().__init__(parent)

        if self.parent.config.add_layers and self.parent.config.layers is None:
            raise LayersNotFound(
                "add_layers is set to True but no layers are provided."
            )

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

        model = getattr(models, self.parent.PYTORCH_MODEL)(
            pretrained=self.parent.config.pretrained
        )
        for param in model.parameters():
            param.require_grad = self.parent.config.trainable

        if self.parent.config.add_layers:
            layers = [
                create_layer(value)
                for key, value in self.parent.config.layers.items()
            ]

            if self.parent.LAST_LAYER_TYPE == "classifier_sequential":
                if len(layers) > 1:
                    layers = [nn.Sequential(*layers)]
                model.classifier = nn.Sequential(
                    *list(model.classifier.children())[:-1] + layers
                )
            elif self.parent.LAST_LAYER_TYPE == "classifier_linear":
                if len(layers) == 1:
                    model.classifier = layers[0]
                elif len(layers) > 1:
                    model.classifier = nn.Sequential(*layers)
            else:
                if len(layers) == 1:
                    model.fc = layers[0]
                elif len(layers) > 1:
                    model.fc = nn.Sequential(*layers)

        self._model = model.to(self.device)

        return self._model

    def set_model_parameters(self):
        if self.parent.LAST_LAYER_TYPE == "classifier_sequential":
            self.model_parameters = (
                self._model.parameters()
                if self.parent.config.trainable
                else self._model.classifier[-1].parameters()
            )
        elif self.parent.LAST_LAYER_TYPE == "classifier_linear":
            self.model_parameters = (
                self._model.parameters()
                if self.parent.config.trainable
                else self._model.classifier.parameters()
            )
        else:
            self.model_parameters = (
                self._model.parameters()
                if self.parent.config.trainable
                else self._model.fc.parameters()
            )


class PyTorchPreTrainedModel(Model):
    def __init__(self, config) -> None:
        super().__init__(config)


for model_name, name, last_layer_type in [
    ("alexnet", "AlexNet", "classifier_sequential"),
    ("densenet121", "DenseNet121", "classifier_linear"),
    ("densenet161", "DenseNet161", "classifier_linear"),
    ("densenet169", "DenseNet169", "classifier_linear"),
    ("densenet201", "DenseNet201", "classifier_linear"),
    ("mnasnet0_5", "MnasNet0_5", "classifier_sequential"),
    ("mnasnet1_0", "MnasNet1_0", "classifier_sequential"),
    ("mobilenet_v2", "MobileNetV2", "classifier_sequential"),
    ("vgg11", "VGG11", "classifier_sequential"),
    ("vgg11_bn", "VGG11BN", "classifier_sequential"),
    ("vgg13", "VGG13", "classifier_sequential"),
    ("vgg13_bn", "VGG13BN", "classifier_sequential"),
    ("vgg16", "VGG16", "classifier_sequential"),
    ("vgg16_bn", "VGG16BN", "classifier_sequential"),
    ("vgg19", "VGG19", "classifier_sequential"),
    ("vgg19_bn", "VGG19BN", "classifier_sequential"),
    ("googlenet", "GoogleNet", "fully_connected"),
    ("inception_v3", "InceptionV3", "fully_connected"),
    ("resnet101", "ResNet101", "fully_connected"),
    ("resnet152", "ResNet152", "fully_connected"),
    ("resnet18", "ResNet18", "fully_connected"),
    ("resnet34", "ResNet34", "fully_connected"),
    ("resnet50", "ResNet50", "fully_connected"),
    ("resnext101_32x8d", "ResNext101_32x8D", "fully_connected"),
    ("resnext50_32x4d", "ResNext50_32x4D", "fully_connected"),
    ("shufflenet_v2_x0_5", "ShuffleNetV2x0_5", "fully_connected"),
    ("shufflenet_v2_x1_0", "ShuffleNetV2x1_0", "fully_connected"),
    ("wide_resnet101_2", "WideResNet101_2", "fully_connected"),
    ("wide_resnet50_2", "WideResNet50_2", "fully_connected"),
]:
    cls_config = type(
        name + "ModelConfig", (PyTorchPreTrainedModelConfig,), {},
    )
    cls_context = type(name + "ModelContext", (PyTorchPretrainedContext,), {},)

    dffml_cls = type(
        name + "Model",
        (PyTorchPreTrainedModel,),
        {
            "CONFIG": cls_config,
            "CONTEXT": cls_context,
            "PYTORCH_MODEL": model_name,
            "LAST_LAYER_TYPE": last_layer_type,
        },
    )

    dffml_cls = entrypoint(model_name)(dffml_cls)

    setattr(sys.modules[__name__], cls_config.__qualname__, cls_config)
    setattr(sys.modules[__name__], cls_context.__qualname__, cls_context)
    setattr(sys.modules[__name__], dffml_cls.__qualname__, dffml_cls)
