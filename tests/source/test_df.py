from dffml.source.df import DataFlowSource, DataFlowSourceConfig
from dffml.util.asynctestcase import AsyncTestCase
from dffml.feature import Features, Feature
from dffml.source.source import Sources
from dffml.source.memory import MemorySource, MemorySourceConfig
from dffml.record import Record
from dffml.df.base import op
from dffml.df.types import Input, DataFlow, Definition, InputFlow
from dffml.operation.output import AssociateDefinition


edit_feature_def = Definition(name="feature_data", primitive="generic")


@op(
    name="edit_feature",
    inputs={"features": edit_feature_def},
    outputs={"updated_features": edit_feature_def},
)
async def edit_feature(features):
    value = features * 10
    return {"updated_features": value}


FEATURE_DATA = [
    [0, 1, 0.1, 10],
    [1, 3, 0.2, 20],
    [2, 5, 0.3, 30],
    [3, 7, 0.4, 40],
]
A, B, C, D = list(zip(*FEATURE_DATA))
NEW_RECORDS = [
    Record(
        str(i),
        data={
            "features": {
                "Years": A[i] * 10,
                "Expertise": B[i] * 10,
                "Trust": C[i] * 10,
                "Salary": D[i] * 10,
            }
        },
    )
    for i in range(len(A))
]

TEST_FEATURE = Features(
    Feature("Years", int, 1),
    Feature("Expertise", int, 1),
    Feature("Trust", float, 1),
    Feature("Salary", int, 1),
)

TEST_DATAFLOW1 = DataFlow(
    operations={
        "edit_feature": edit_feature,
        "associate_definition": AssociateDefinition,
    },
    flow={
        "edit_feature": InputFlow(
            inputs={
                "features": [
                    {"seed": ["Years", "Expertise", "Trust", "Salary"]}
                ]
            },
        ),
        "associate_definition": InputFlow(inputs={"spec": ["seed"]}),
    },
)
TEST_DATAFLOW1.seed = [
    # I don't think we need this as we are providing the flow
    Input(
        value={
            feature.name: edit_feature.op.outputs["updated_features"].name
            for feature in TEST_FEATURE
        },
        definition=AssociateDefinition.op.inputs["spec"],
    )
]


class TestDataFlowSource(AsyncTestCase):
    @classmethod
    def setUpClass(self):
        self.records = [
            Record(
                str(i),
                data={
                    "features": {
                        "Years": A[i],
                        "Expertise": B[i],
                        "Trust": C[i],
                        "Salary": D[i],
                    }
                },
            )
            for i in range(4)
        ]
        self.source = Sources(
            MemorySource(MemorySourceConfig(records=self.records))
        )

    def config(self, source, dataflow, features):
        return DataFlowSourceConfig(
            source=source, dataflow=dataflow, features=features,
        )

    def setUpSource(self):
        return DataFlowSource(
            self.config(
                source=self.source,
                dataflow=TEST_DATAFLOW1,
                features=TEST_FEATURE,
            )
        )

    async def test_records(self):
        records = {}
        async with self.setUpSource() as source:
            async with source() as dfsctx:
                async for record in dfsctx.records():
                    records[int(record.key)] = record
        for i, record in enumerate(NEW_RECORDS):
            with self.subTest(i=i):
                self.assertDictEqual(record.features(), records[i].features())
