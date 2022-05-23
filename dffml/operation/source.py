from typing import List, Dict, Any

from ..df.base import op
from ..base import config
from ..df.types import Definition
from ..source.source import BaseSource


@config
class SourceOperationConfig:
    source: BaseSource


@op(
    inputs={
        "features": Definition(name="features", primitive="List[str]"),
        "predict_features": Definition(
            name="predict_features", primitive="List[str]"
        ),
    },
    outputs={
        "matrix": Definition(name="matrix", primitive="List[List[Any]]"),
        "keys": Definition(name="keys", primitive="List[str]"),
        "unprocessed_matrix": Definition(
            name="unprocessed_matrix", primitive="List[List[Any]]"
        ),
    },
    config_cls=SourceOperationConfig,
    imp_enter={"source": (lambda self: self.config.source)},
    ctx_enter={"sctx": (lambda self: self.parent.source())},
)
async def convert_records_to_list(self, features, predict_features):
    matrix = []
    keys = []
    unprocessed_matrix = []
    async for record in self.sctx.records():
        keys.append(record.key)
        matrix.append([record.feature(feature) for feature in features])
        unprocessed_matrix.append(
            [record.feature(feature) for feature in predict_features]
        )
    return {
        "keys": keys,
        "matrix": matrix,
        "unprocessed_matrix": unprocessed_matrix,
    }


@op(
    config_cls=SourceOperationConfig,
    expand=["result"],
    imp_enter={"source": (lambda self: self.config.source)},
    ctx_enter={"sctx": (lambda self: self.parent.source())},
)
async def source_records(self, features, predict_features):
    matrix = []
    keys = []
    unprocessed_matrix = []
    async for record in self.sctx.records():
        keys.append(record.key)
        matrix.append([record.feature(feature) for feature in features])
        unprocessed_matrix.append(
            [record.feature(feature) for feature in predict_features]
        )
    return {
        "keys": keys,
        "matrix": matrix,
        "unprocessed_matrix": unprocessed_matrix,
    }


@op(
    inputs={
        "matrix": convert_records_to_list.op.outputs["matrix"],
        "features": convert_records_to_list.op.inputs["features"],
        "keys": convert_records_to_list.op.outputs["keys"],
        "predict_features": convert_records_to_list.op.inputs[
            "predict_features"
        ],
        "unprocessed_matrix": convert_records_to_list.op.outputs[
            "unprocessed_matrix"
        ],
    },
    outputs={
        "records": Definition(name="records", primitive="Dict[str, Any]")
    },
)
def convert_list_to_records(
    keys: List[str],
    matrix: List[List[Any]],
    features: List[str],
    unprocessed_matrix: List[List[Any]],
    predict_features: List[str],
) -> Dict[str, Any]:
    return {
        "records": {
            key: {
                "features": {
                    **{
                        feature: value
                        for feature, value in zip(features, data_row)
                    },
                    **{
                        feature: value
                        for feature, value in zip(
                            predict_features, unprocessed_row
                        )
                    },
                }
            }
            for key, data_row, unprocessed_row in zip(
                keys, matrix, unprocessed_matrix
            )
        }
    }
