import json
import yaml
import asyncio
import copy


from dffml import (
    op,
    DataFlow,
    Input,
    InputFlow,
    MemoryOrchestrator,
    Feature,
    Definition,
    Features,
    GetSingle,
    run_dataflow,
    RunDataFlowConfig,
)

from dffml.configloader.configloader import ConfigLoaders
from dffml.db.sqlite import SqliteDatabase, SqliteDatabaseConfig

from dffml.df.base import op
from dffml.operation.mapping import (
    mapping_extract_value,
    create_mapping,
    mapping_merge,
    group_mappings,
)
from dffml.operation.model import model_predict, ModelPredictConfig
from dffml.operation.db import (
    DatabaseQueryConfig,
    db_query_insert,
)

from dffml_source_mysql.db import (
    MySQLDatabase,
    MySQLDatabaseConfig,
)

from dffml_model_tensorflow.dnnc import (
    DNNClassifierModel,
    DNNClassifierModelConfig,
)

from feature.git.dffml_feature_git.feature.definitions import *
from dffml.operation.output import GroupBy


async def main():
    subflow_yaml = "./cgi-bin/dataflow.yaml"
    async with ConfigLoaders() as cfgl:
        _, subflow = await cfgl.load_file(filepath=subflow_yaml)
    subflow = DataFlow._fromdict(**subflow)

    # We want to create a dataflow which runs the
    # subflow and use the outputs of the subflow as
    # features to run inference on a trained model,
    # and add the prediction of the model to a database.

    prediction_df = DataFlow(
        operations={
            run_dataflow.op.name: run_dataflow,
            GetSingle.op.name: GetSingle,
            model_predict.op.name: model_predict,
            group_mappings.op.name: group_mappings,
            db_query_insert.op.name: db_query_insert,
            "mapping_extract_value": mapping_extract_value.op,
            "create_key_mapping": create_mapping.op,
            "create_maintained_mapping": create_mapping.op,
            "create_insert_data": mapping_merge,
        }
    )

    prediction_df.configs[db_query_insert.op.name] = DatabaseQueryConfig(
        database=MySQLDatabase(
            MySQLDatabaseConfig(
                host="127.0.0.1",
                port=3306,
                user="user",
                password="pass",
                db="db",
                ca=None,
            )
        )
    )
    prediction_df.configs[run_dataflow.op.name] = RunDataFlowConfig(
        dataflow=subflow
    )
    prediction_df.configs[model_predict.op.name] = ModelPredictConfig(
        model=DNNClassifierModel(
            DNNClassifierModelConfig(
                predict=Feature("maintained", int, 1),
                classifications=[0, 1],
                features=Features(
                    Feature("authors", int, 10),
                    Feature("commits", int, 10),
                    Feature("work", int, 10),
                ),
            )
        )
    )
    # Modifying run_dataflow to take URL as input and output the features
    prediction_df.operations[run_dataflow.op.name] = run_dataflow.op._replace(
        inputs={"URL": URL},
        outputs={
            "authors": author_count,
            "commits": commit_count,
            "work": work_spread,
        },
        expand=[],
    )
    # Modyfing group_mapping to gather the features (results of the subflow)
    prediction_df.operations[
        group_mappings.op.name
    ] = group_mappings.op._replace(
        inputs={
            "authors": author_count,
            "commits": commit_count,
            "work": work_spread,
        },
        outputs={"results": model_predict.op.inputs["features"]},
    )

    # For inserting the prediction to the database,
    # we need the table_name and data of the form
    # {"key": URL , "maintained": 0/1}
    # To create this we create each key,value map as
    # an individual dictionary and merge them.

    # Modyfing an instance of create_mapping to take URL definition as
    # value, so that a dictionary of the form {"key":URL} is the output.
    prediction_df.operations[
        "create_key_mapping"
    ] = create_mapping.op._replace(
        inputs={"key": create_mapping.op.inputs["key"], "value": URL}
    )

    prediction_df.seed.extend(
        [
            # To create a key value mapping "maintained" : value
            #  model_predict outputs: {'model_predictions': {'maintained':
            # {'confidence': 0.9989588260650635, 'value': '1'}}}
            #  we need to extract the 'value' from it.
            Input(
                value="maintained",
                definition=create_mapping.op.inputs["key"],
                origin="seed.maintained",
            ),
            Input(
                value=["maintained", "value"],
                definition=mapping_extract_value.op.inputs["traverse"],
                origin="seed.traverse",
            ),
            #  To create a key value mapping "key" : URL
            Input(
                value="key",
                definition=create_mapping.op.inputs["key"],
                origin="seed.key",
            ),
            # The table to insert
            Input(
                value="status",
                definition=db_query_insert.op.inputs["table_name"],
            ),
        ],
    )

    prediction_df.update(auto_flow=True)

    # Directing output of group_mapping to be input of model_prediction
    prediction_df.flow[model_predict.op.name] = InputFlow(
        inputs={"features": [{group_mappings.op.name: "results"}]}
    )

    prediction_df.flow["mapping_extract_value"] = InputFlow(
        inputs={
            "traverse": ["seed.traverse"],
            "mapping": [{model_predict.op.name: "prediction"}],
        }
    )

    # Create maintained mapping
    prediction_df.flow["create_maintained_mapping"] = InputFlow(
        inputs={
            "key": ["seed.maintained"],
            "value": [{"mapping_extract_value": "value"}],
        }
    )

    # Create key mapping
    prediction_df.flow["create_key_mapping"] = InputFlow(
        inputs={"key": ["seed.key"], "value": ["seed"]}
    )

    # Merge key and maintained mappings to create data for insert
    prediction_df.flow["create_insert_data"] = InputFlow(
        inputs={
            "one": [{"create_key_mapping": "mapping"}],
            "two": [{"create_maintained_mapping": "mapping"}],
        }
    )

    prediction_df.flow[db_query_insert.op.name] = InputFlow(
        inputs={
            "table_name": ["seed"],
            "data": [{"create_insert_data": "mapping"}],
        }
    )
    prediction_df.update()

    exported = prediction_df.export()
    with open("prediction_df.yaml", "w+") as f:
        yaml.dump(exported, f)

    prediction_df = DataFlow._fromdict(**exported)

    test_inputs = {
        "interactive_wall": [
            Input(
                value="https://github.com/eirslett/test-git-repo",
                definition=URL,
            )
        ]
    }

    async with MemoryOrchestrator.withconfig({}) as orchestrator:
        async with orchestrator(prediction_df) as octx:
            async for _ctx, results in octx.run(test_inputs):
                print("Done")


if __name__ == "__main__":
    asyncio.run(main())
