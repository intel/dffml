from __future__ import print_function, division

import sys
import torch.nn as nn
from torchvision import models

from dffml.util.entrypoint import entrypoint
from dffml.model.model import Model
from .pytorch_base import PyTorchModelConfig, PyTorchModelContext


class PyTorchPretrainedContext(PyTorchModelContext):
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

        model = getattr(models, self.parent.PYTORCH_MODEL)(
            pretrained=self.parent.config.pretrained
        )
        for param in model.parameters():
            param.require_grad = self.parent.config.trainable

        if self.parent.LAST_LAYER_TYPE == "classifier_sequential":
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

        elif self.parent.LAST_LAYER_TYPE == "classifier_linear":
            model.classifier = nn.Sequential(
                nn.Linear(model.classifier.in_features, 256),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(256, len(self.classifications)),
                nn.LogSoftmax(dim=1),
            )

        else:
            model.fc = nn.Sequential(
                nn.Linear(model.fc.in_features, 256),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(256, len(self.classifications)),
                nn.LogSoftmax(dim=1),
            )

        self._model = model.to(self.device)
        return self._model


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
    cls_config = type(name + "ModelConfig", (PyTorchModelConfig,), {},)
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
