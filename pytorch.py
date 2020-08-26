import torch
import torch.nn as nn
import asyncio

from dffml import DirectorySource, Features, Feature, Sources
from dffml import train, accuracy, predict
from dffml_model_pytorch.pytorch_net import (
    PyTorchNeuralNetwork,
    PyTorchNeuralNetworkConfig,
)


# class ConvNet(nn.Module):
#     def __init__(self):
#         super(ConvNet, self).__init__()
#         self.conv1 = nn.Conv2d(3, 6, 5)
#         self.pool = nn.MaxPool2d(2, 2)
#         self.conv2 = nn.Conv2d(6, 16, 5)
#         self.fc1 = nn.Linear(16 * 5 * 5, 120)
#         self.fc2 = nn.Linear(120, 84)
#         self.fc3 = nn.Linear(84, 10)

#     def forward(self, x):
#         x = self.pool(nn.ReLU()(self.conv1(x)))
#         x = self.pool(nn.ReLU()(self.conv2(x)))
#         x = x.view(-1, 16 * 5 * 5)
#         x = nn.ReLU()(self.fc1(x))
#         x = nn.ReLU()(self.fc2(x))
#         x = self.fc3(x)
#         return x


class ConvNet(nn.Module):
    def __init__(self):
        super(ConvNet, self).__init__()
        self.conv_layer = nn.Sequential(
            # Conv Layer block 1
            nn.Conv2d(
                in_channels=3, out_channels=32, kernel_size=3, padding=1
            ),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.Conv2d(
                in_channels=32, out_channels=64, kernel_size=3, padding=1
            ),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            # Conv Layer block 2
            nn.Conv2d(
                in_channels=64, out_channels=128, kernel_size=3, padding=1
            ),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.Conv2d(
                in_channels=128, out_channels=128, kernel_size=3, padding=1
            ),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Dropout2d(p=0.05),
            # Conv Layer block 3
            nn.Conv2d(
                in_channels=128, out_channels=256, kernel_size=3, padding=1
            ),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.Conv2d(
                in_channels=256, out_channels=256, kernel_size=3, padding=1
            ),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )

        self.fc_layer = nn.Sequential(
            nn.Dropout(p=0.1),
            nn.Linear(4096, 1024),
            nn.ReLU(inplace=True),
            nn.Linear(1024, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.1),
            nn.Linear(512, 10),
        )

    def forward(self, x):
        """Perform forward."""

        # conv layers
        x = self.conv_layer(x)

        # flatten
        x = x.view(x.size(0), -1)

        # fc layer
        x = self.fc_layer(x)

        return x


model = PyTorchNeuralNetwork(
    features=Features(Feature("image", int, 500 * 500)),
    predict=Feature("label", int, 1),
    directory="test_dir",
    trainable=True,
    network="/home/tron/Desktop/dffml/modelcifar.yaml",
    configloader="yaml",
    epochs=1,
    imageSize=32,
    classifications=[
        "airplane",
        "automobile",
        "bird",
        "cat",
        "deer",
        "dog",
        "frog",
        "horse",
        "ship",
        "truck",
    ],
)

train_source = DirectorySource(
    foldername="/home/tron/Desktop/Development/cifar/dataset/train",
    feature="image",
    labels=[
        "airplane",
        "automobile",
        "bird",
        "cat",
        "deer",
        "dog",
        "frog",
        "horse",
        "ship",
        "truck",
    ],
)

test_source = DirectorySource(
    foldername="/home/tron/Desktop/Development/cifar/dataset/testing",
    feature="image",
    labels=[
        "airplane",
        "automobile",
        "bird",
        "cat",
        "deer",
        "dog",
        "frog",
        "horse",
        "ship",
        "truck",
    ],
)


async def main():
    await train(model, test_source)


asyncio.run(main())
