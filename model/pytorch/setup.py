import os
import importlib.util
from setuptools import setup

# Boilerplate to load commonalities
spec = importlib.util.spec_from_file_location(
    "setup_common", os.path.join(os.path.dirname(__file__), "setup_common.py")
)
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)

common.KWARGS["entry_points"] = {
    "dffml.model": [
        "pytorchnet = dffml_model_pytorch.pytorch_net:PyTorchNeuralNetwork",
        "alexnet = dffml_model_pytorch.pytorch_pretrained:AlexNetModel",
        "densenet121 = dffml_model_pytorch.pytorch_pretrained:DenseNet121Model",
        "densenet161 = dffml_model_pytorch.pytorch_pretrained:DenseNet161Model",
        "densenet169 = dffml_model_pytorch.pytorch_pretrained:DenseNet169Model",
        "densenet201 = dffml_model_pytorch.pytorch_pretrained:DenseNet201Model",
        "mnasnet0_5 = dffml_model_pytorch.pytorch_pretrained:MnasNet0_5Model",
        "mnasnet1_0 = dffml_model_pytorch.pytorch_pretrained:MnasNet1_0Model",
        "mobilenet_v2 = dffml_model_pytorch.pytorch_pretrained:MobileNetV2Model",
        "vgg11 = dffml_model_pytorch.pytorch_pretrained:VGG11Model",
        "vgg11_bn = dffml_model_pytorch.pytorch_pretrained:VGG11BNModel",
        "vgg13 = dffml_model_pytorch.pytorch_pretrained:VGG13Model",
        "vgg13_bn = dffml_model_pytorch.pytorch_pretrained:VGG13BNModel",
        "vgg16 = dffml_model_pytorch.pytorch_pretrained:VGG16Model",
        "vgg16_bn = dffml_model_pytorch.pytorch_pretrained:VGG16BNModel",
        "vgg19 = dffml_model_pytorch.pytorch_pretrained:VGG19Model",
        "vgg19_bn = dffml_model_pytorch.pytorch_pretrained:VGG19BNModel",
        "googlenet = dffml_model_pytorch.pytorch_pretrained:GoogleNetModel",
        "inception_v3 = dffml_model_pytorch.pytorch_pretrained:InceptionV3Model",
        "resnet101 = dffml_model_pytorch.pytorch_pretrained:ResNet101Model",
        "resnet152 = dffml_model_pytorch.pytorch_pretrained:ResNet152Model",
        "resnet18 = dffml_model_pytorch.pytorch_pretrained:ResNet18Model",
        "resnet34 = dffml_model_pytorch.pytorch_pretrained:ResNet34Model",
        "resnet50 = dffml_model_pytorch.pytorch_pretrained:ResNet50Model",
        "resnext101_32x8d = dffml_model_pytorch.pytorch_pretrained:ResNext101_32x8DModel",
        "resnext50_32x4d = dffml_model_pytorch.pytorch_pretrained:ResNext50_32x4DModel",
        "shufflenet_v2_x0_5 = dffml_model_pytorch.pytorch_pretrained:ShuffleNetV2x0_5Model",
        "shufflenet_v2_x1_0 = dffml_model_pytorch.pytorch_pretrained:ShuffleNetV2x1_0Model",
        "wide_resnet101_2 = dffml_model_pytorch.pytorch_pretrained:WideResNet101_2Model",
        "wide_resnet50_2 = dffml_model_pytorch.pytorch_pretrained:WideResNet50_2Model",
    ]
}

setup(**common.KWARGS)
