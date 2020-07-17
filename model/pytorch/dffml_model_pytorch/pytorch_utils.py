from __future__ import print_function, division

import torch
from torchvision import transforms


class NumpyToTensor(torch.utils.data.Dataset):
    def __init__(self, data, target=None):
        self.data = data
        self.target = target

    def transform(self, data):
        return transforms.Compose(
            [
                transforms.ToPILImage(),
                transforms.Resize(250),
                transforms.CenterCrop((250, 250)),
                transforms.ToTensor(),
                transforms.Normalize(
                    [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]
                ),
            ]
        )(data)

    def __getitem__(self, index):
        x = self.transform(self.data[index])

        if self.target is not None:
            y = self.target[index]
            return x, y
        else:
            return x

    def __len__(self):
        return len(self.data)
