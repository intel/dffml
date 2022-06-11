import sys
import json
import asyncio
import pathlib
import platform
import textwrap
from typing import Dict, List, Any, NewType

import dffml


# Our data types
ThreatModelImageURL = NewType("ThreatModelImageURL", dict)
ThreatDragonThreatModel = NewType("ThreatDragonThreatModel", dict)
ThreatDragonThreatModelPath = NewType("ThreatDragonThreatModelPath", pathlib.Path)
ThreatsMarkdown = NewType("ThreatsMarkdown", str)
ThreatsMdPath = NewType("ThreatsMdPath", str)
# Tested on Python 3.9.2 (list rather than typing.List)
ThreatModelSections = NewType("ThreatModelSections", list[str])


@dffml.op
def load_threat_dragon_model(
    threat_dragon_filepath: ThreatDragonThreatModelPath,
) -> ThreatDragonThreatModel:
    # Read in the file
    contents = pathlib.Path(threat_dragon_filepath).read_text()
    # Load the contents
    # TODO(security) Validate using JSON schema before accessing properties
    return json.loads(contents)


@dffml.op
def threats_dragon_diagram_url(
    threat_dragon_threat_model: ThreatDragonThreatModel,
) -> ThreatModelImageURL:
    # TODO Run playwright to generate diagram. Not working in WSL.
    async def todo():
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto("https://www.threatdragon.com/#/local/threatmodel/import")
            print(await page.title())
            await browser.close()

    # return await image_data_from_playwright()
    # TODO Upload to server? httptest?

    return "https://user-images.githubusercontent.com/5950433/173202578-d2d5495b-8c4a-4383-9577-0e807ef442eb.png"


@dffml.op(
    name="generate_threat_model_sections",
    inputs={
        "threat_dragon_threat_model": ThreatDragonThreatModel,
        "threat_model_image_url": ThreatModelImageURL,
    },
    outputs={"result": ThreatModelSections,},
)
class GenerateThreatModelSections(dffml.OperationImplementationContext):
    async def run(self, inputs: Dict[str, Any]) -> Dict[str, List[str]]:
        return {"result": [str(value) for value in inputs.values()]}


@dffml.op
def write_out_threats_md(
    output_filepath: ThreatsMdPath, threat_model_sections: ThreatModelSections,
):
    pathlib.Path(output_filepath).write_text(
        textwrap.dedent(
            """
            # Threat Model

            """
        )
        + "\n".join(threat_model_sections)
    )


THREATS_MD_DATAFLOW = dffml.DataFlow(*dffml.opimp_in(sys.modules[__name__]),)


async def main():
    # async for results in scanner():
    async for _ctx, results in dffml.run(
        THREATS_MD_DATAFLOW,
        {
            arg: [
                dffml.Input(
                    value=arg,
                    definition=dffml_feature_git.feature.definitions.URL,
                    # definition=InputOfUnknownType,
                ),
            ]
            for arg in sys.argv[1:]
        },
    ):
        print(_ctx, results)


if __name__ == "__main__":
    asyncio.run(main())
