import aiosqlite
from collections import OrderedDict
from typing import AsyncIterator, NamedTuple, Dict

from dffml.base import BaseConfig
from dffml.repo import Repo
from dffml.source.source import BaseSourceContext, BaseSource
from dffml.util.cli.arg import Arg

class CustomSQLiteSourceConfig(BaseConfig, NamedTuple):
    filename: str

class CustomSQLiteSourceContext(BaseSourceContext):

    async def update(self, repo: Repo):
        db = self.parent.db
        # Store feature data
        feature_cols = self.parent.FEATURE_COLS
        feature_data = OrderedDict.fromkeys(feature_cols)
        feature_data.update(repo.features(feature_cols))
        await db.execute('INSERT OR REPLACE INTO features (src_url, ' + \
                         ', '.join(feature_cols) + ') '
                         'VALUES(?, ' + \
                         ', '.join('?' * len(feature_cols)) +
                         ')',
                         [repo.src_url] + list(feature_data.values()))
        # Store prediction
        prediction = repo.prediction()
        if prediction:
            prediction_cols = self.parent.PREDICTION_COLS
            prediction_data = OrderedDict.fromkeys(prediction_cols)
            prediction_data.update(prediction.dict())
            await db.execute('INSERT OR REPLACE INTO prediction (src_url, ' + \
                             ', '.join(prediction_cols) + ') '
                             'VALUES(?, ' + \
                             ', '.join('?' * len(prediction_cols)) +
                             ')',
                             [repo.src_url] + list(prediction_data.values()))
        # Store classification
        if repo.classified():
            await db.execute('INSERT OR REPLACE INTO classification '
                             '(src_url, classification) VALUES(?, ?)',
                             [repo.src_url, repo.classification()])

    async def repos(self) -> AsyncIterator[Repo]:
        # NOTE This logic probably isn't what you want. Only for demo purposes.
        src_urls = await self.parent.db.execute('SELECT src_url FROM features')
        for row in await src_urls.fetchall():
            yield await self.repo(row['src_url'])

    async def repo(self, src_url: str):
        db = self.parent.db
        repo = Repo(src_url)
        # Get features
        features = await db.execute('SELECT ' + \
                                    ', '.join(self.parent.FEATURE_COLS) + ' '
                                    'FROM features WHERE src_url=?',
                                    (repo.src_url,))
        features = await features.fetchone()
        if features is not None:
            repo.evaluated(features)
        # Get prediction
        prediction = await db.execute('SELECT * FROM prediction WHERE '
                                      'src_url=?', (repo.src_url,))
        prediction = await prediction.fetchone()
        if prediction is not None:
            repo.predicted(prediction['classification'],
                           prediction['confidence'])
        # Get classification
        classification = await db.execute('SELECT * FROM classification WHERE '
                                      'src_url=?', (repo.src_url,))
        classification = await classification.fetchone()
        if classification is not None:
            repo.classify(classification['classification'])
        return repo

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.parent.db.commit()

class CustomSQLiteSource(BaseSource):

    CONTEXT = CustomSQLiteSourceContext
    FEATURE_COLS = ['PetalLength', 'PetalWidth', 'SepalLength', 'SepalWidth']
    PREDICTION_COLS = ['classification', 'confidence']
    CLASSIFICATION_COLS = ['classification']

    async def __aenter__(self) -> 'BaseSourceContext':
        self.__db = aiosqlite.connect(self.config.filename)
        self.db = await self.__db.__aenter__()
        self.db.row_factory = aiosqlite.Row
        # Create table for feature data
        await self.db.execute('CREATE TABLE IF NOT EXISTS features ('
                              'src_url TEXT PRIMARY KEY NOT NULL, ' + \
                              (' REAL, '.join(self.FEATURE_COLS)) + \
                              ' REAL'
                              ')')
        # Create table for predictions
        await self.db.execute('CREATE TABLE IF NOT EXISTS prediction ('
                              'src_url TEXT PRIMARY KEY, ' + \
                              'classification TEXT, '
                              'confidence REAL'
                              ')')
        # Create table for classification
        await self.db.execute('CREATE TABLE IF NOT EXISTS classification ('
                              'src_url TEXT PRIMARY KEY, ' + \
                              'classification TEXT'
                              ')')
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.__db.__aexit__(exc_type, exc_value, traceback)

    @classmethod
    def args(cls, args, *above) -> Dict[str, Arg]:
        cls.config_set(args, above, 'filename', Arg())
        return args

    @classmethod
    def config(cls, config, *above):
        return SQLiteSourceConfig(
            filename=cls.config_get(config, above, 'filename'),
            )
