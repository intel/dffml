'''
Uses Tensorflow to create a generic DNN which learns on all of the features in a
repo.
'''
import os
import asyncio
import hashlib
import numpy as np
import tensorflow
from typing import List, Dict, Any, AsyncIterator, Tuple, Optional

from dffml.repo import Repo
from dffml.feature import Feature, Features
from dffml.source import Sources
from dffml.model import Model
from dffml.accuracy import Accuracy

from .log import LOGGER

LOGGER = LOGGER.getChild('dnn')

class DNN(Model):
    '''
    Model using tensorflow to make predictions. Handels creation of feature
    columns for real valued, string, and list of real valued features.
    '''

    def __init__(self):
        super().__init__()
        self._model = None
        # Load packages with lots of dependencies durring instantiation so that
        # users can choose to install these or not.
        self.__np = np
        self._tf = tensorflow

    def mkclassifications(self, classifications):
        classifications = {value: key for key, value in \
                self.mkcids(classifications).items()}
        LOGGER.debug('classifications(%d): %r', len(classifications),
                classifications)
        return classifications

    def mkcids(self, classifications):
        cids = dict(zip(range(0, len(classifications)),
            sorted(classifications)))
        LOGGER.debug('cids(%d): %r', len(cids), cids)
        return cids

    async def applicable_features(self, features: Features):
        usable = await self.features(features)
        return [name for name in features.names() if name in usable]

    async def training_input_fn(self, sources: Sources, features: Features,
            classifications: List[Any],
            batch_size=20, shuffle=False, num_epochs=1, **kwargs):
        '''
        Uses the numpy input function with data from repo features.
        '''
        classifications = self.mkclassifications(classifications)
        features = await self.applicable_features(features)
        LOGGER.debug('Training on features: %r', features)
        x_cols: Dict[str, Any] = {feature: [] for feature in features}
        y_cols = []
        for repo in [repo async for repo in \
                sources.classified_with_features(features) \
                if repo.classification() in classifications]:
            for feature, results in repo.features(features).items():
                x_cols[feature].append(self.__np.array(results))
            y_cols.append(classifications[repo.classification()])
        presplit = len(y_cols)
        if not presplit:
            raise ValueError('No repos to train on')
        split = 0.7
        split = int(float(presplit) * split)
        y_cols = self.__np.array(y_cols[:split])
        for feature in x_cols:
            x_cols[feature] = self.__np.array(x_cols[feature][:split])
        LOGGER.info('------ Repo Data ------')
        LOGGER.info('total:     %d', presplit)
        LOGGER.info('x_cols:    %d', len(list(x_cols.values())[0]))
        LOGGER.info('y_cols:    %d', len(y_cols))
        LOGGER.info('-----------------------')
        input_fn = self._tf.estimator.inputs.numpy_input_fn(x_cols,
                y_cols, batch_size=batch_size,
                shuffle=shuffle, num_epochs=num_epochs, **kwargs)
        return input_fn

    async def accuracy_input_fn(self, sources: Sources, features: Features,
            classifications: List[Any],
            batch_size=20, shuffle=False, num_epochs=1, **kwargs):
        '''
        Uses the numpy input function with data from repo features.
        '''
        features = await self.applicable_features(features)
        classifications = self.mkclassifications(classifications)
        x_cols: Dict[str, Any] = {feature: [] for feature in features}
        y_cols = []
        for repo in [repo async for repo in \
                sources.classified_with_features(features) \
                if repo.classification() in classifications]:
            for feature, results in repo.features(features).items():
                x_cols[feature].append(self.__np.array(results))
            y_cols.append(classifications[repo.classification()])
        presplit = len(y_cols)
        split = 0.7
        split = int(float(presplit) * split)
        y_cols = self.__np.array(y_cols[split:])
        for feature in x_cols:
            x_cols[feature] = self.__np.array(x_cols[feature][split:])
        LOGGER.info('------ Repo Data ------')
        LOGGER.info('total:     %d', presplit)
        LOGGER.info('x_cols:    %d', len(list(x_cols.values())[0]))
        LOGGER.info('y_cols:    %d', len(y_cols))
        LOGGER.info('-----------------------')
        input_fn = self._tf.estimator.inputs.numpy_input_fn(x_cols,
                y_cols, batch_size=batch_size,
                shuffle=shuffle, num_epochs=num_epochs, **kwargs)
        return input_fn

    async def predict_input_fn(self, repos: AsyncIterator[Repo],
            features: Features, classifications: List[Any], **kwargs):
        '''
        Uses the numpy input function with data from repo features.
        '''
        features = await self.applicable_features(features)
        classifications = self.mkclassifications(classifications)
        x_cols: Dict[str, Any] = {feature: [] for feature in features}
        ret_repos = []
        async for repo in repos:
            if not repo.features(features):
                continue
            ret_repos.append(repo)
            for feature, results in repo.features(features).items():
                x_cols[feature].append(self.__np.array(results))
        for feature in x_cols:
            x_cols[feature] = self.__np.array(x_cols[feature])
        LOGGER.info('------ Repo Data ------')
        LOGGER.info('x_cols:    %d', len(list(x_cols.values())[0]))
        LOGGER.info('-----------------------')
        input_fn = self._tf.estimator.inputs.numpy_input_fn(x_cols,
                shuffle=False, num_epochs=1, **kwargs)
        return input_fn, ret_repos

    async def features(self, features: Features):
        '''
        Converts repos into training data
        '''
        cols: Dict[str, Any] = {}
        for feature in features:
            col = self.feature_feature_column(feature)
            if not col is None:
                cols[feature.NAME] = col
        return cols

    def feature_feature_column(self, feature: Feature):
        '''
        Creates a feature column for a feature
        '''
        dtype = feature.dtype()
        if dtype is int or issubclass(dtype, int) \
                or dtype is float or issubclass(dtype, float):
            return self._tf.feature_column.numeric_column(feature.NAME,
                    shape=feature.length())
        LOGGER.warning('Unknown dtype %r. Cound not create column' % (dtype))
        return None

    def model_dir_path(self, features: Features):
        '''
        Creates the path to the model dir by using the provided model dir and
        the sha256 hash of the concatenated feature names.
        '''
        if self.model_dir is None:
            return None
        model = hashlib.sha256(''.join(features.names()).encode('utf-8'))\
                .hexdigest()
        if not os.path.isdir(self.model_dir):
            raise NotADirectoryError('%s is not a directory' % (self.model_dir))
        return os.path.join(self.model_dir, model)

    async def model(self, features: Features, classifications: List[Any]):
        '''
        Generates or loads a model
        '''
        if self._model is not None:
            return self._model
        # Build 3 layer DNN with 10, 20, 10 units respectively.
        # 2 classifications whitelist or blacklist
        LOGGER.debug('Loading model with classifications(%d): %r',
                len(classifications), classifications)
        self._model = self._tf.estimator.DNNClassifier(
                feature_columns=list((await self.features(features)).values()),
                hidden_units=[10, 20, 10],
                n_classes=len(classifications),
                model_dir=self.model_dir_path(features))
        return self._model

    async def train(self, sources: Sources, features: Features,
            classifications: List[Any], steps: int, num_epochs: int):
        '''
        Train on data submitted via classify.
        '''
        input_fn = await self.training_input_fn(sources, features,
                classifications,
                batch_size=20, shuffle=True, num_epochs=num_epochs)
        (await self.model(features, classifications))\
                .train(input_fn=input_fn, steps=steps)

    async def accuracy(self, sources: Sources, features: Features,
            classifications: List[Any]) -> Accuracy:
        '''
        Evaluates the accuracy of our model after training using the input repos
        as test data.
        '''
        if not os.path.isdir(self.model_dir_path(features)):
            raise NotADirectoryError('Model not trained')
        input_fn = await self.accuracy_input_fn(sources, features,
                classifications,
                batch_size=20, shuffle=False, num_epochs=1)
        accuracy_score = (await self.model(features, classifications))\
                .evaluate(input_fn=input_fn)
        return Accuracy(accuracy_score['accuracy'])

    async def predict(self, repos: AsyncIterator[Repo], features: Features,
            classifications: List[Any]) -> \
                    AsyncIterator[Tuple[Repo, Any, float]]:
        '''
        Uses trained data to make a prediction about the quality of a repo.
        '''
        if not os.path.isdir(self.model_dir_path(features)):
            raise NotADirectoryError('Model not trained')
        cids = self.mkcids(classifications)
        # Create the input function
        input_fn, predict = await self.predict_input_fn(repos, features,
                classifications)
        # Makes predictions on classifications
        predictions = (await self.model(features, classifications))\
                .predict(input_fn=input_fn)
        for repo, pred_dict in zip(predict, predictions):
            class_id = pred_dict['class_ids'][0]
            probability = pred_dict['probabilities'][class_id]
            yield repo, cids[class_id], probability
