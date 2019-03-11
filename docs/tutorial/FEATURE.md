# New Feature Tutorial

## Create the Package

To create a new feature we first create a new python package. DFFML has a script
to created it for you.

We're going to create a feature that multiplies float values by `4.2`.

```console
export YOUR_FEATURE_NAME=string
./scripts/new_feature.sh $YOUR_FEATURE_NAME
```

> All lower case, only underscores allowed.

This creates a package in which multiple features could live. We start with just
one the `MiscFeature` which is now located in
`/path/to/dffml/feature/$YOUR_FEATURE_NAME/feature/misc.py`.

## Name the first feature

```console
mv feature/$YOUR_FEATURE_NAME/dffml_feature_$YOUR_FEATURE_NAME/feature/misc.py \
  feature/$YOUR_FEATURE_NAME/dffml_feature_$YOUR_FEATURE_NAME/feature/string_by_4_point_2.py
```

Open the file for editing and continue.

### Class Name

Our feature multiplies strings by 4.2 so lets give it a name that says that.

```python
class StringBy4Point2Feature(Feature):
    '''
    Multiplies strings that are floats by 4.2
    '''

    LOGGER = LOGGER.getChild('StringBy4Point2Feature')

    NAME: str = 'string_by_4_point_2'
```

### DType

Set the data type to float.

```python
    def dtype(self) -> Type:
        return float
```

### Length

The length stays at 1.

```python
    def length(self) -> int:
        return 1
```

### Applicable

This feature is only applicable if the string can be made into a float. Since
the quickest way to do this for our demo is to cast it, we'll store the result
while we're at it.

```python
    async def applicable(self, data) -> bool:
        try:
            await data.data.set('as_float', float(data.src_url))
            return True
        except ValueError:
            return False
```

### Fetch

Applicable will have already stored the data as a float, therefore there is no
fetch needed.

```python
    async def fetch(self, data):
        pass
```

### Parse

Applicable will have already stored the data as a float, therefore there is no
parse needed because the data has already been parsed.

```python
    async def parse(self, data):
        pass
```

### Calc

Calculation is where we retrieve the parsed value and multiply it by `4.2`.

```python
    async def calc(self, data):
        '''
        Calculates the score for this feature based on data found by parse().
        '''
        return 4.2 * (await data.data.get('as_float'))
```

## Correct the plugin load path

Since we changed the name from `misc` to `string_by_4_point_2`, we have to
change the path in `setup.py` which will load our feature.

```python
    entry_points={
        'dffml.feature': [
            'string_by_4_point_2 = dffml_feature_string.feature.string_by_4_point_2:StringBy4Point2Feature',
        ],
    },
```

## Test the new feature

Lets modify the test case to verify that we did this right.

### Change the import path

```python
from dffml_feature_string.feature.string_by_4_point_2 import \
  StringBy4Point2Feature
```

### Modify `evaluates` test

The tests start out with one testcase which should work. Modify that so that it
still works. If you don't it should fail because the string being parsed can't
be parsed into a float.

```python
    async def test_string_evaluates(self):
        async with FEATURES:
            for src_url in ['10.0']:
```

### Add a test for correct multiplication

The `evaluates` test just checks that the feature runs. Let's make sure it
correctly multiplies.

```python
    async def test_string_by_4_point_2(self):
            for src_url in ['10.0']:
                with self.subTest(src_url=src_url):
                    features = await FEATURES.evaluate(src_url)
                    self.assertEqual(len(features.values()), len(FEATURES))
                    self.assertEqual(sum(features.values()), 42)
```

### Run the tests

```console
cd feature/$YOUR_FEATURE_NAME
python3.7 setup.py test
```
