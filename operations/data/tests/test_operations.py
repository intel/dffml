import numpy as np
from sklearn.datasets import make_classification

from dffml.df.types import Input, DataFlow
from dffml.operation.output import GetSingle
from dffml.df.memory import MemoryOrchestrator
from dffml.util.asynctestcase import AsyncTestCase
from sklearn.feature_selection import f_classif
from dffml_operations_data.operations import *


class TestOperations(AsyncTestCase):
    async def test_principal_component_analysis(self):
        input_data, _ = make_classification(
            n_samples=10,
            n_features=10,
            n_informative=8,
            n_redundant=2,
            random_state=7,
        )
        async for ctx, results in MemoryOrchestrator.run(
            DataFlow.auto(principal_component_analysis, GetSingle),
            [
                Input(
                    value=[
                        principal_component_analysis.op.outputs["result"].name
                    ],
                    definition=GetSingle.op.inputs["spec"],
                ),
                Input(
                    value=input_data,
                    definition=principal_component_analysis.op.inputs["data"],
                ),
                Input(
                    value=8,
                    definition=principal_component_analysis.op.inputs[
                        "n_components"
                    ],
                ),
            ],
        ):
            self.assertTrue(
                (10, 8)
                == results[
                    principal_component_analysis.op.outputs["result"].name
                ].shape
            )

    async def test_singular_value_decomposition(self):
        input_data, _ = make_classification(
            n_samples=10,
            n_features=10,
            n_informative=8,
            n_redundant=2,
            random_state=7,
        )
        async for ctx, results in MemoryOrchestrator.run(
            DataFlow.auto(singular_value_decomposition, GetSingle),
            [
                Input(
                    value=[
                        singular_value_decomposition.op.outputs["result"].name
                    ],
                    definition=GetSingle.op.inputs["spec"],
                ),
                Input(
                    value=input_data,
                    definition=singular_value_decomposition.op.inputs["data"],
                ),
                Input(
                    value=8,
                    definition=singular_value_decomposition.op.inputs[
                        "n_components"
                    ],
                ),
                Input(
                    value=1,
                    definition=singular_value_decomposition.op.inputs[
                        "n_iter"
                    ],
                ),
                Input(
                    value=7,
                    definition=singular_value_decomposition.op.inputs[
                        "random_state"
                    ],
                ),
            ],
        ):
            self.assertTrue(
                (10, 8)
                == results[
                    singular_value_decomposition.op.outputs["result"].name
                ].shape,
            )

    async def test_simple_imputer(self):
        input_data = [[np.nan, 2], [6, np.nan], [7, 6]]
        output_data = [[6.5, 2], [6, 4], [7, 6]]
        async for ctx, results in MemoryOrchestrator.run(
            DataFlow.auto(simple_imputer, GetSingle),
            [
                Input(
                    value=[simple_imputer.op.outputs["result"].name],
                    definition=GetSingle.op.inputs["spec"],
                ),
                Input(
                    value=input_data,
                    definition=simple_imputer.op.inputs["data"],
                ),
                Input(
                    value=np.nan,
                    definition=simple_imputer.op.inputs["missing_values"],
                ),
                Input(
                    value="mean",
                    definition=simple_imputer.op.inputs["strategy"],
                ),
            ],
        ):
            self.assertTrue(
                (
                    results[simple_imputer.op.outputs["result"].name]
                    == output_data
                ).all()
            )

    async def test_one_hot_encoder(self):
        categories = [["Male", "Female"], [1, 2, 3]]
        input_data = [["Female", 1], ["Male", 3]]
        output_data = [[0.0, 1.0, 1.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0, 1.0]]
        async for ctx, results in MemoryOrchestrator.run(
            DataFlow.auto(one_hot_encoder, GetSingle),
            [
                Input(
                    value=[one_hot_encoder.op.outputs["result"].name],
                    definition=GetSingle.op.inputs["spec"],
                ),
                Input(
                    value=input_data,
                    definition=one_hot_encoder.op.inputs["data"],
                ),
                Input(
                    value=categories,
                    definition=one_hot_encoder.op.inputs["categories"],
                ),
            ],
        ):
            self.assertTrue(
                (
                    results[one_hot_encoder.op.outputs["result"].name]
                    == output_data
                ).all()
            )

    async def test_standard_scaler(self):
        input_data = [[0, 0], [0, 0], [1, 1], [1, 1]]
        output_data = [[-1, -1], [-1, -1], [1, 1], [1, 1]]
        async for ctx, results in MemoryOrchestrator.run(
            DataFlow.auto(standard_scaler, GetSingle),
            [
                Input(
                    value=[standard_scaler.op.outputs["result"].name],
                    definition=GetSingle.op.inputs["spec"],
                ),
                Input(
                    value=input_data,
                    definition=standard_scaler.op.inputs["data"],
                ),
            ],
        ):
            self.assertTrue(
                (
                    results[standard_scaler.op.outputs["result"].name]
                    == output_data
                )
            )

    async def test_remove_whitespaces(self):
        input_data = [["  ABC ", "XYD   "], ["  ABC", "   XYD "]]
        output_data = [["ABC", "XYD"], ["ABC", "XYD"]]
        async for ctx, results in MemoryOrchestrator.run(
            DataFlow.auto(remove_whitespaces, GetSingle),
            [
                Input(
                    value=[remove_whitespaces.op.outputs["result"].name],
                    definition=GetSingle.op.inputs["spec"],
                ),
                Input(
                    value=input_data,
                    definition=remove_whitespaces.op.inputs["data"],
                ),
            ],
        ):
            self.assertTrue(
                (
                    results[remove_whitespaces.op.outputs["result"].name]
                    == output_data
                ).all()
            )

    async def test_ordinal_encoder(self):
        input_data = [["x", "a"], ["x", "b"], ["y", "a"]]
        output_data = [
            [1.0, 0.0, 1.0, 0.0],
            [1.0, 0.0, 0.0, 1.0],
            [0.0, 1.0, 1.0, 0.0],
        ]
        async for ctx, results in MemoryOrchestrator.run(
            DataFlow.auto(ordinal_encoder, GetSingle),
            [
                Input(
                    value=[ordinal_encoder.op.outputs["result"].name],
                    definition=GetSingle.op.inputs["spec"],
                ),
                Input(
                    value=input_data,
                    definition=ordinal_encoder.op.inputs["data"],
                ),
            ],
        ):
            self.assertTrue(
                (
                    results[ordinal_encoder.op.outputs["result"].name]
                    == output_data
                ).all()
            )

    async def test_select_k_best(self):
        input_data = [[1, 1], [1, 2], [1, 1], [0, 2], [1, 1], [1, 1]]
        target_data = [1,2,1,2,1,2]
        output_data = [[1], [2], [1], [2], [1], [1]]

        async for ctx, results in MemoryOrchestrator.run(
            DataFlow.auto(select_k_best, GetSingle),
            [
                Input(
                    value=[select_k_best.op.outputs["result"].name],
                    definition=GetSingle.op.inputs["spec"],
                ),
                Input(
                    value=input_data,
                    definition=select_k_best.op.inputs["data"],
                ),
                Input(
                    value=target_data,
                    definition=select_k_best.op.inputs["target_data"],
                ),
                Input(
                    value=f_classif,
                    definition=select_k_best.op.inputs["score_func"],
                ),
                Input(
                    value=1,
                    definition=select_k_best.op.inputs["k"],
                ),
            ],
        ):
            self.assertTrue(
                (
                    results[select_k_best.op.outputs["result"].name]
                    == output_data
                ).all()
            )
    async def test_select_percentile(self):
        input_data = [[1, 1], [1, 2], [1, 1], [0, 2], [1, 1], [1, 1]]
        target_data = [1,2,1,2,1,2]
        output_data = [[1], [2], [1], [2], [1], [1]]

        async for ctx, results in MemoryOrchestrator.run(
            DataFlow.auto(select_percentile, GetSingle),
            [
                Input(
                    value=[select_percentile.op.outputs["result"].name],
                    definition=GetSingle.op.inputs["spec"],
                ),
                Input(
                    value=input_data,
                    definition=select_percentile.op.inputs["data"],
                ),
                Input(
                    value=target_data,
                    definition=select_percentile.op.inputs["target_data"],
                ),
                Input(
                    value=f_classif,
                    definition=select_percentile.op.inputs["score_func"],
                ),
                Input(
                    value=50,
                    definition=select_percentile.op.inputs["percentile"],
                ),
            ],
        ):
            self.assertTrue(
                (
                    results[select_percentile.op.outputs["result"].name]
                    == output_data
                ).all()
            )