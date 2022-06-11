import json
import pathlib

from ...record import Record
from ..memory import MemorySource
from .base import dataset_source


@dataset_source("owasp.threat-dragon")
async def threat_dragon(
    filepath: pathlib.Path,
    feature_name: str = "threat_model",
    schema_url: str = "https://github.com/OWASP/threat-dragon/raw/1.6.2/docs/development/schema/owasp.threat-dragon.schema.json",
    format_version: str = "1.0.0",
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
    if format_version is None:
        format_version = "1.0.0"
    # Read in the file
    contents = filepath.read_text()
    # Load the contents
    threat_model_dict = json.loads(contents)
    # TODO(security) Validate using JSON schema before accessing properties
    title = threat_model_dict["summary"]["title"]
    yield MemorySource(
        records=[
            Record(
                key=title,
                data={"features": {feature_name: threat_model_dict}},
                extra={
                    "open-architecture": {
                        "features": {
                            feature_name: {
                                "manifest_metadata": {
                                    "schema": schema_url,
                                    "format_name": threat_dragon.source.ENTRY_POINT_LABEL,
                                    "format_version": format_version,
                                },
                                "extra": {
                                    "dffml": {
                                        "source": threat_dragon.source.ENTRY_POINT_LABEL,
                                    },
                                },
                            },
                        },
                    },
                },
            )
        ],
    )
