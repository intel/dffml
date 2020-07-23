import os
import io
import json
import unittest.mock
import tempfile


from dffml import (
    op,
    config,
    Definition,
    DataFlow,
    Input,
    MemoryOrchestrator,
    GetSingle,
    AsyncTestCase,
    Feature,
    Model,
    ModelContext,
    Record,
    SqliteDatabase,
    SqliteDatabaseConfig,
    db_query_update,
    DatabaseQueryConfig,
    run_dataflow,
    RunDataFlowConfig,
    model_predict,
    ModelPredictConfig,
)
from dffml import Accuracy as AccuracyType

from tests.test_df import DATAFLOW, add, mult, parse_line
from tests.test_cli import FakeFeature
from typing import List, Dict, Any, Optional, Tuple, AsyncIterator

from dffml.util.entrypoint import entrypoint
from dffml.df.base import op
from dffml.operation.mapping import (
    mapping_expand_all_values,
    mapping_expand_all_keys,
    mapping_extract_value,
    create_mapping,
)
from dffml.operation.array import array_create, array_append


@config
class FakeModelConfig:
    feature: Feature
    predict: Feature


# Model
class FakeModelContext(ModelContext):
    async def train(self, *args, **kwargs):
        pass

    async def accuracy(self, *args, **kwargs):
        return AccuracyType(0.5)

    async def predict(
        self, records: AsyncIterator[Record]
    ) -> AsyncIterator[Record]:
        async for record in records:
            record.predicted(
                self.parent.config.feature.name,
                record.feature(self.parent.config.feature.name) + 0.1234,
                0.5,
            )
            yield record


@entrypoint("fake")
class FakeModel(Model):
    CONTEXT = FakeModelContext
    CONFIG = FakeModelConfig


class TestRunOnDataflow(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        fileno, cls.database_name = tempfile.mkstemp(suffix=".db")
        os.close(fileno)
        cls.sdb = SqliteDatabase(
            SqliteDatabaseConfig(filename=cls.database_name)
        )
        cls.table_name = "fakeTable"

    @classmethod
    def tearDownClass(cls):
        os.unlink(cls.database_name)

    async def setUp(self):
        super().setUp()
        async with SqliteDatabase(
            SqliteDatabaseConfig(filename=self.database_name)
        ) as db:
            async with db() as ctx:
                await ctx.create_table(
                    self.table_name, {"key": "text", "value": "int"}
                )
                await ctx.insert(
                    self.table_name, {"key": "add_op", "value": 0}
                )
                await ctx.insert(
                    self.table_name, {"key": "mult_op", "value": 0}
                )

    async def test_run(self):
        test_dataflow = DataFlow(
            operations={
                "run_dataflow": run_dataflow.op,
                "get_single": GetSingle.imp.op,
                "model_predict": model_predict.op,
                "mapping_expand_all_values": mapping_expand_all_values.op,
                "mapping_expand_all_keys": mapping_expand_all_keys.op,
                "mapping_extract_value": mapping_extract_value.op,
                "create_value_mapping": create_mapping.op,
                "conditions_array_create": array_create.op,
                "conditions_array_append_1": array_append.op,
                "conditions_array_append_2": array_append.op,
                "conditions_or": array_create.op,
                "conditions_and": array_create.op,
                "update_db": db_query_update.op,
            },
            configs={
                "run_dataflow": RunDataFlowConfig(dataflow=DATAFLOW),
                "model_predict": ModelPredictConfig(
                    model=FakeModel(
                        FakeModelConfig(
                            feature=Feature("result", int, 1),
                            predict=Feature("fakePrediction", float, 1),
                        )
                    )
                ),
                "update_db": DatabaseQueryConfig(database=self.sdb),
            },
            seed=[
                # Make the output of the dataflow the prediction
                # model_predict outputs: {"mapping":
                #   {'confidence': 0.5, 'value': 4200}}
                # we need to extract the 'value' from it.
                # We could also do this by creating a mapping_remove_key
                # operation and removing the 'confidence' key, then merging with
                # the string to parse.
                Input(
                    value=["result", "value"],
                    definition=mapping_extract_value.op.inputs["traverse"],
                ),
                # Create a key value mapping where the key is "value"
                # {'value': 4200}
                Input(
                    value="value",
                    definition=create_mapping.op.inputs["key"],
                    origin="seed.create_value_mapping.key",
                ),
                # Create the conditions array for the db update operation
                Input(
                    value="key",
                    definition=array_append.op.inputs["value"],
                    origin="seed.conditions.index.0",
                ),
                Input(
                    value="=",
                    definition=array_append.op.inputs["value"],
                    origin="seed.conditions.index.1",
                ),
                # The table to update
                Input(
                    value=self.table_name,
                    definition=db_query_update.op.inputs["table_name"],
                ),
            ],
            implementations={
                "model_predict": model_predict.imp,
                mapping_expand_all_values.op.name: mapping_expand_all_values.imp,
                mapping_expand_all_keys.op.name: mapping_expand_all_keys.imp,
                create_mapping.op.name: create_mapping.imp,
                mapping_extract_value.op.name: mapping_extract_value.imp,
                array_create.op.name: array_create.imp,
                array_append.op.name: array_append.imp,
                db_query_update.op.name: db_query_update.imp,
            },
        )
        # Redirect output of run_dataflow to model_predict
        test_dataflow.flow["mapping_expand_all_keys"].inputs["mapping"] = [
            {"run_dataflow": "results"}
        ]
        test_dataflow.flow["mapping_expand_all_values"].inputs["mapping"] = [
            {"run_dataflow": "results"}
        ]
        test_dataflow.flow["model_predict"].inputs["features"] = [
            {"mapping_expand_all_values": "value"}
        ]
        test_dataflow.flow["mapping_extract_value"].inputs["mapping"] = [
            {"model_predict": "prediction"}
        ]
        # Create value mapping
        test_dataflow.flow["create_value_mapping"].inputs["key"] = [
            "seed.create_value_mapping.key"
        ]
        test_dataflow.flow["create_value_mapping"].inputs["value"] = [
            {"mapping_extract_value": "value"}
        ]
        # Create db update conditions array
        test_dataflow.flow["conditions_array_create"].inputs["value"] = [
            "seed.conditions.index.0"
        ]
        test_dataflow.flow["conditions_array_append_1"].inputs.update(
            {
                "array": [{"conditions_array_create": "array"}],
                "value": ["seed.conditions.index.1"],
            }
        )
        test_dataflow.flow["conditions_array_append_2"].inputs.update(
            {
                "array": [{"conditions_array_append_1": "array"}],
                "value": [{"mapping_expand_all_keys": "key"}],
            }
        )
        # Nest the condition array in the
        # ((key = ?) OR (1 = 1)) AND ((1 = 1))
        # Format that the update operation requires
        test_dataflow.flow["conditions_or"].inputs.update(
            {"value": [{"conditions_array_append_2": "array"}]}
        )
        test_dataflow.flow["conditions_and"].inputs.update(
            {"value": [{"conditions_or": "array"}]}
        )
        # Use key value mapping as data for db update
        test_dataflow.flow["update_db"].inputs.update(
            {
                "data": [{"create_value_mapping": "mapping"}],
                "conditions": [{"conditions_and": "array"}],
            }
        )

        test_dataflow.update_by_origin()

        test_inputs = [
            {
                "add_op": [
                    {
                        "value": "add 40 and 2",
                        "definition": parse_line.op.inputs["line"].name,
                    },
                    {
                        "value": [add.op.outputs["sum"].name],
                        "definition": GetSingle.op.inputs["spec"].name,
                    },
                ]
            },
            {
                "mult_op": [
                    {
                        "value": "multiply 42 and 10",
                        "definition": parse_line.op.inputs["line"].name,
                    },
                    {
                        "value": [mult.op.outputs["product"].name],
                        "definition": GetSingle.op.inputs["spec"].name,
                    },
                ]
            },
        ]
        test_outputs = {"add_op": 42.1234, "mult_op": 420.1234}

        async with MemoryOrchestrator.withconfig({}) as orchestrator:
            async with orchestrator(test_dataflow) as octx:
                async for _ctx, results in octx.run(
                    {
                        list(test_input.keys())[0]: [
                            Input(
                                value=test_input,
                                definition=run_dataflow.op.inputs["inputs"],
                            )
                        ]
                        for test_input in test_inputs
                    }
                ):
                    pass

        async with SqliteDatabase(
            SqliteDatabaseConfig(filename=self.database_name)
        ) as db:
            async with db() as db_ctx:
                results = {
                    row["key"]: row["value"]
                    async for row in db_ctx.lookup(self.table_name)
                }
                for key, value in test_outputs.items():
                    with self.subTest(context=key):
                        self.assertIn(key, results)
                        self.assertEqual(value, results[key])
