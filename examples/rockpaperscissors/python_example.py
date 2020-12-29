import torch.nn as nn
import asyncio
import logging

from dffml import train, accuracy, predict, DirectorySource, Features, Feature
from dffml_model_pytorch import PyTorchNeuralNetwork, CrossEntropyLossFunction


# Define the Neural Network
class ConvNet(nn.Module):
    """
    Convolutional Neural Network to classify hand gestures in an image as rock, paper or scissors
    """

    def __init__(self):
        super(ConvNet, self).__init__()

        self.conv1 = nn.Conv2d(
            in_channels=3, out_channels=32, kernel_size=5, padding=2
        )
        self.conv2 = nn.Conv2d(
            in_channels=32, out_channels=32, kernel_size=3, padding=1
        )
        self.conv3 = nn.Conv2d(
            in_channels=32, out_channels=16, kernel_size=3, padding=1
        )

        self.relu = nn.ReLU()
        self.pooling = nn.MaxPool2d(kernel_size=2)

        self.linear = nn.Linear(in_features=16 * 9 * 9, out_features=3)

    def forward(self, x):
        # block 1
        x = self.pooling(self.relu(self.conv1(x)))

        # block 2
        x = self.pooling(self.relu(self.conv2(x)))

        # block 3
        x = self.pooling(self.relu(self.conv2(x)))

        # block 4
        x = self.pooling(self.relu(self.conv3(x)))

        # fully connected layer
        x = self.linear(x.view(-1, 16 * 9 * 9))
        return x


RockPaperScissorsModel = ConvNet()
Loss = CrossEntropyLossFunction()

# Define the dffml model config
model = PyTorchNeuralNetwork(
    classifications=["rock", "paper", "scissors"],
    features=Features(Feature("image", int, 300 * 300)),
    predict=Feature("label", int, 1),
    directory="rps_model",
    network=RockPaperScissorsModel,
    epochs=10,
    batch_size=32,
    imageSize=150,
    validation_split=0.2,
    loss=Loss,
    optimizer="Adam",
    enableGPU=True,
    patience=2,
)

# Define source for training image dataset
train_source = DirectorySource(
    foldername="rps", feature="image", labels=["rock", "paper", "scissors"],
)

# Define source for testing image dataset
test_source = DirectorySource(
    foldername="rps-test-set",
    feature="image",
    labels=["rock", "paper", "scissors"],
)

# Define source for prediction image dataset
predict_source = DirectorySource(foldername="rps-predict", feature="image",)


async def main():
    logging.basicConfig(level=logging.DEBUG)

    # Train the model
    await train(model, train_source)

    logging.getLogger().setLevel(logging.CRITICAL)

    # Assess the accuracy
    acc = await accuracy(model, test_source)
    print("\nTesting Accuracy: ", acc)

    # Make Predictions
    print(
        "\n{:>40} \t {:>10} \t {:>10}\n".format(
            "Image filename", "Prediction", "Confidence"
        )
    )
    async for key, features, prediction in predict(model, predict_source):
        print(
            "{:>40} \t {:>10} \t {:>10}".format(
                "rps-predict/" + key,
                prediction["label"]["value"],
                prediction["label"]["confidence"],
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
