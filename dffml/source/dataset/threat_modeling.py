import json
import pathlib

from ...record import Record
from ..memory import MemorySource
from .base import dataset_source


@dataset_source("owasp.threat-dragon")
async def threat_dragon(
    filepath: pathlib.Path, feature_name: str = "threat_model",
):
    r"""
    Examples
    --------

    .. code-block:: console
        :test:

        $ dffml list records -sources threat_model=owasp.threat-dragon \
            -source-threat_model-filepath /home/pdxjohnny/Documents/python/living-threat-models/models/good.json

    >>> from dffml.noasync import load
    >>> from dffml import iris_training
    >>>
    >>> records = list(load(iris_training.source()))
    >>> print(len(records))
    120
    >>> records[0].export()
    {'key': '0', 'features': {'SepalLength': 6.4, 'SepalWidth': 2.8, 'PetalLength': 5.6, 'PetalWidth': 2.2, 'classification': 2}, 'extra': {}}
    """
    contents = filepath.read_text()
    threat_model_dict = json.loads(contents)
    # TODO(security) Validate JSON schema
    title = threat_model_dict["summary"]["title"]
    yield MemorySource(
        records=[
            Record(
                key=title,
                data={"features": {feature_name: threat_model_dict,},},
            )
        ],
    )
