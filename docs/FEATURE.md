# Feature

Features are given a repo, containing at the minimum a source URL for it,
and produce a list of results which represent the evaluation of that feature.

Not all methods are applicable to all repos. As such, all Features implement the
`applicable` method.

Feature is the abstract base class for all features. New features must be
derived from this class and implement the fetch, parse, and calc methods. These
methods are always called in order by the evaluator. However, they are executed
in parallel with the same stages of other features.

A feature is provided with a repo
and is expected to fetch any data it needs to calculate itself when fetch
is called. All data fetched should be stored in tempdir() if it must reside
on disk.

Once the appropriate data is fetched the parse method is responsible for
storing the parts of that data which will be used to calculate in the
subclass

```python
from dffml.feature import Feature

class StringByFT(Feature):

    async def fetch(self):
        self.__value = '42'

    async def parse(self):
        self.__value = int(self.__value)
```

The calc method then uses variables set in parse to calculate the feature.

```python
async def calc(self):
    return self.__value * 42
```

```python
entry_points={
    'dffml.feature': [
        'string_by_42 = mypackage.string_by_42:StringByFT',
    ],
},
```
