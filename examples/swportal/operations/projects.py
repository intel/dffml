import pathlib

import yaml
from dffml import op, DataFlow

DATAFLOW_DIRECTORY = pathlib.Path(__file__).parent.parent / "projects" / "df"
EXPORT_SEED_DEFINITIONS = ("uuid", "name")
NON_PROJECT_DATAFLOWS = ("projects",)


@op
def projects() -> dict:
    return {
        path.stem: {
            i.definition.name: i.value
            for i in DataFlow._fromdict(
                **yaml.safe_load(path.read_text())
            ).seed
            if i.definition.name in EXPORT_SEED_DEFINITIONS
        }
        for path in DATAFLOW_DIRECTORY.glob("*.yaml")
        if path.stem not in NON_PROJECT_DATAFLOWS
    }
