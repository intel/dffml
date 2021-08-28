import asyncio

from operations import *

from dffml import *


city_state_pairs = [
    ("Phoenix city", "Arizona"),
    ("Miami city", "Florida"),
    ("Orlando city", "Florida"),
    ("Portland city (pt.)", "Oregon"),
    ("Las Vegas city", "Nevada"),
    ("Seattle city", "Washington"),
    ("Chicago city", "Illinois"),
]

features = Features(
    Feature("city", str, 1),
    Feature("state", str, 1),
    Feature("month", int, 1),
)

records = []

for i, (city, state) in enumerate(city_state_pairs):
    for j, month in enumerate(range(1, 13)):
        records.append(
            Record(
                str(i * 100 + j),
                data={
                    "features": {"city": city, "state": state, "month": month,}
                },
            )
        )

dataflow = DataFlow(
    operations={
        "lookup_temperature": lookup_temperature,
        "lookup_population": lookup_population,
        "generate_sales": generate_sales,
    }
)

dataflow.flow.update(
    {
        "lookup_temperature": InputFlow(
            inputs={
                "city": [{"seed": ["city"]}],
                "month": [{"seed": ["month"]}],
            }
        ),
        "lookup_population": InputFlow(
            inputs={
                "city": [{"seed": ["city"]}],
                "state": [{"seed": ["state"]}],
            }
        ),
        "generate_sales": InputFlow(
            inputs={
                "population": [{"lookup_population": "population"}],
                "temperature": [{"lookup_temperature": "temperature"}],
                "month": [{"seed": ["month"]}],
            }
        ),
    }
)
dataflow.update()
mem_source = Sources(MemorySource(MemorySourceConfig(records=records)))

source = DataFlowPreprocessSource(
    DataFlowPreprocessSourceConfig(
        source=mem_source, dataflow=dataflow, features=features,
    )
)


async def main():
    async for record in load(source):
        print(record.features())


if __name__ == "__main__":
    asyncio.run(main())
