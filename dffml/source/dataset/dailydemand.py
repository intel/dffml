import pathlib

from ..csv import CSVSource
from .base import dataset_source
from ...util.net import cached_download
from ...util.file import find_replace_with_hash_validation


@dataset_source("dailydemand.training")
async def dailydemand_training(
    cache_dir: pathlib.Path = (
        pathlib.Path("~", ".cache", "dffml", "datasets", "dailydemand")
        .expanduser()
        .resolve()
    )
):
    """
    Examples
    --------

    .. code-block:: console
        :test:

        $ dffml list records -sources training=dailydemand.training

    >>> from dffml.noasync import load
    >>> from dffml import dailydemand_training
    >>>
    >>> records = list(load(dailydemand_training.source()))
    >>> print(len(records))
    60
    >>> records[0].export()
    {'key': '0', 'features': {'Week': 1, 'Day': 4, 'Non-urgent order': 316.307, 'Urgent order': 223.270, 'A': 61.543, 'B': 175.586, 'C': 302.448, 'Fiscal sector order': 0, 'traffic controller sector order': 65556, 'Banking Order-1': 44914, 'Banking Order-2': 188411, 'Banking Order-3': 14793, 'Target': 539.577}, 'extra': {}}

    """
    original_path = await cached_download(
        "https://archive.ics.uci.edu/ml/machine-learning-databases/00409/Daily_Demand_Forecasting_Orders.csv",
        cache_dir / "training_original.csv",
        "b3a0101ae409ec8c9eeae74a509905dbdd1c7a9d6b674e86ae875a4a387c3002b8b3603b0aa1d15de0d87701ee209c14",
        protocol_allowlist=["https://"],
    )
    # Create a CSV source using header replaced file
    yield CSVSource(
        filename=str(
            find_replace_with_hash_validation(
                original_path,
                cache_dir / "training.csv",
                r"Week of the month (first week, second, third, fourth or fifth week;Day of the week (Monday to Friday);Non-urgent order;Urgent order;Order type A;Order type B;Order type C;Fiscal sector orders;Orders from the traffic controller sector;Banking orders (1);Banking orders (2);Banking orders (3);Target (Total orders)",
                "Week; Day; Non-urgent order; Urgent order; A; B; C; Fiscal sector order; traffic controller sector order; Banking Order-1; Banking Order-2; Banking Order-3, Target",
                expected_sha384_hash="946d1bb691d6a2ca5037028a0c6ac29d68f4026e293fd64f985a61cf31fb72b19d50baa61038398442430db8af926bbd",
            )
        )
    )
