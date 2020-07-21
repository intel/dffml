from __future__ import print_function, division

import torch
from torchvision import transforms


class NumpyToTensor(torch.utils.data.Dataset):
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
