# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
'''
Description of what this model does
'''
import os
import hashlib
from typing import AsyncIterator, Tuple, Any, List, Optional

from dffml.repo import Repo
from dffml.source import Sources
from dffml.feature import Features
from dffml.accuracy import Accuracy
from dffml.model import Model

import torch
import torch.nn as nn
from torch.utils import data as torch_data

from sklearn.metrics import accuracy_score


from .log import LOGGER

LOGGER = LOGGER.getChild('fcdn')


class Net(nn.Module):

    def __init__(self, in_dim, out_dim):

        super().__init__()

        self.layers = nn.Sequential(
            nn.Linear(in_dim, 15),
            nn.ReLU(inplace=True),
            nn.Linear(15, 100),
            nn.ReLU(inplace=True),
            nn.Linear(100, out_dim),
            nn.Softmax(dim=1)
        )

    def forward(self, x):

        return self.layers(x)


class DFCN(Model):
    '''
    Model wraping pytorch API
    '''

    def __init__(self, model_dir: Optional[str] = None) -> None:
        super().__init__()
        self.model_dir = model_dir
        self._torch = torch
        self._model = None

    async def prepare_dataset(self, sources: Sources, features: Features, classifications: List[Any]):

        feature_names = features.names()
        raw_data = [repo async for repo in sources.classified_with_features(feature_names)]
        _, cids = self.mkcids(classifications)

        xs, ys = [], []
        for repo in raw_data:
            x, y = self.transform_repo(repo, feature_names, cids)
            xs.append(torch.tensor(x).float())
            ys.append(y)

        return torch_data.DataLoader(
            list(zip(xs, ys)),
            batch_size=20,
            shuffle=True
        )

    def transform_repo(self, repo: Repo, feature_names: List[Any], cids: dict):

        return tuple(repo.features(feature_names).values()), cids[repo.classification()]

    def model_file_path(self, features: Features):

        if self.model_dir is None:
            return None

        model = hashlib.sha256(''.join(features.names()).encode('utf-8'))\
            .hexdigest()
        if not os.path.isdir(self.model_dir):
            raise NotADirectoryError('%s is not a directory' % (self.model_dir))
        return os.path.join(self.model_dir, model, 'model.pth.tar')

    def mkcids(self, classifications: List[Any]):

        num_to_label = dict(enumerate(sorted(classifications)))
        label_to_num = {v: k for k, v in num_to_label.items()}
        return num_to_label, label_to_num

    def model(self, features: Features, classifications: List[Any], pretrained: bool= False):

        if self._model is not None:
            return self._model

        self._model = Net(len(features.names()), len(classifications))

        if pretrained:

            model_file_path = self.model_file_path(features)

            if model_file_path is not None:
                LOGGER.debug('Loading pretrained state dict from {}'.format(model_file_path))
                self._model.load_state_dict(torch.load(model_file_path))

        return self._model

    async def train(self, sources: Sources, features: Features,
                    classifications: List[Any], steps: int, num_epochs: int):
        '''
        Train using repos as the data to learn from.
        '''
        model = self.model(features, classifications)
        criterion = nn.CrossEntropyLoss()  # cross entropy loss

        optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

        dataset = await self.prepare_dataset(sources, features, classifications)

        for epoch in range(3000):

            for xs, ys in dataset:
                optimizer.zero_grad()
                out = model(xs)
                loss = criterion(out, ys)
                loss.backward()
                optimizer.step()

            if epoch % 100 == 0:
                print('number of epochs', epoch, 'loss', loss.item())

        model_file_path = self.model_file_path(features)
        if model_file_path is not None:
            LOGGER.debug('Saving state dict to {}'.format(model_file_path))
            torch.save(
                model.state_dict(),
                model_file_path
            )

    async def accuracy(self, sources: Sources, features: Features,
                       classifications: List[Any]) -> Accuracy:
        '''
        Evaluates the accuracy of our model after training using the input repos
        as test data.
        '''
        model = self.model(features, classifications, pretrained=True).eval()
        dataset = await self.prepare_dataset(sources, features, classifications)

        ys, predicted_ys = [], []
        for x, y in dataset:
            _, predicted = torch.max(model(x), 1)
            ys.append(y)
            predicted_ys.append(predicted)

        return accuracy_score(torch.cat(ys, 0).data, torch.cat(predicted_ys, 0).data)

    async def predict(self, repos: AsyncIterator[Repo], features: Features,
                      classifications: List[Any]) -> \
            AsyncIterator[Tuple[Repo, Any, float]]:
        '''
        Uses trained data to make a prediction about the quality of a repo.
        '''

        model = self.model(features, classifications, pretrained=True).eval()
        feature_names = features.names()
        num_to_label, cids = self.mkcids(classifications)

        async for repo in repos:
            x, y = self.transform_repo(repo, feature_names, cids)
            x = torch.tensor([x]).float()
            y = torch.tensor([y]).long()
            val, predicted = torch.max(model(x), 1)
            yield repo, num_to_label[predicted.item()], val.item()
