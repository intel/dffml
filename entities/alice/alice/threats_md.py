import io
import sys
import json
import asyncio
import pathlib
import platform
import textwrap
import contextlib
from typing import Dict, List, Any, NewType

import dffml
import dffml
import dffml.cli.dataflow
import dffml.service.dev

import dffml_config_yaml.configloader


# Our data types
ThreatModelImageURL = NewType("ThreatModelImageURL", dict)
ThreatDragonThreatModel = NewType("ThreatDragonThreatModel", dict)
ThreatDragonThreatModelPath = NewType("ThreatDragonThreatModelPath", pathlib.Path)
ThreatsMarkdown = NewType("ThreatsMarkdown", str)
ThreatsMdPath = NewType("ThreatsMdPath", str)
# Tested on Python 3.9.2 (list rather than typing.List)
ThreatModelSections = NewType("ThreatModelSections", list[str])
OpenArchitectureDiagram = NewType("OpenArchitectureDiagram", list[str])
OpenArchitecture = NewType("OpenArchitecture", list[str])
OpenArchitectureJSON = NewType("OpenArchitectureJSON", list[str])


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
def threat_dragon_diagram_url(
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


@dffml.op
def threat_dragon_threat_model_to_open_architecture(
    self, threat_dragon_threat_model: ThreatDragonThreatModel,
) -> OpenArchitecture:
    return self.octx.config.dataflow


@dffml.op
async def open_architecture_mermaid_diagram(
    open_architecture: OpenArchitecture,
) -> OpenArchitectureDiagram:
    # The overlayed keyword arguements of fields within to be created
    field_modifications = {
        "dataflow": {"default_factory": lambda: open_architecture},
        "simple": {"default": True},
        "stages": {"default_factory": lambda: [dffml.Stage.PROCESSING.value]},
    }
    # Create a derived class
    DiagramForMyDataFlow = dffml.cli.dataflow.Diagram.subclass(
        "DiagramForMyDataFlow", field_modifications,
    )
    a_out = io.StringIO()
    a_out.buffer = io.BytesIO()
    with dffml.chdir(pathlib.Path(__file__).parents[1]):
        with contextlib.redirect_stdout(a_out):
            await DiagramForMyDataFlow._main()

    # TODO FIXME We only have the threat dragon output right now
    return a_out.buffer.getvalue().decode()


@dffml.op
async def open_architecture_as_json(
    open_architecture: OpenArchitectureDiagram,
) -> OpenArchitectureJSON:
    # The overlayed keyword arguements of fields within to be created
    field_modifications = {
        "export": {"default_factory": lambda: "alice.threats_md:THREATS_MD_DATAFLOW"},
        # "configloader": {"default_factory": lambda: dffml_config_yaml.configloader.YamlConfigLoader},
        "configloader": {"default_factory": lambda: dffml.JSONConfigLoader},
    }

    # Create a derived class
    ExportForMyDataFlow = dffml.service.dev.Export.subclass(
        "ExportForMyDataFlow", field_modifications,
    )
    a_out = io.StringIO()
    a_out.buffer = io.BytesIO()
    with contextlib.redirect_stdout(a_out):
        await ExportForMyDataFlow._main()
    return json.dumps(json.loads(a_out.buffer.getvalue().decode()), indent=4)


@dffml.op(
    name="generate_threat_model_sections",
    inputs={
        "threat_model_image_url": ThreatModelImageURL,
        "open_architecture_diagram": OpenArchitectureDiagram,
        "open_architecture_json_dump": OpenArchitectureJSON,
    },
    outputs={"result": ThreatModelSections,},
)
class GenerateThreatModelSections(dffml.OperationImplementationContext):
    async def run(self, inputs: Dict[str, Any]) -> Dict[str, List[str]]:
        # return {"result": [str(value) for value in inputs.values()]}
        return {
            "result": [
                f'![Threat Model Diagram]({inputs["threat_model_image_url"]})',
                (
                    textwrap.dedent(
                        """
                        ```mermaid
                        """
                    )
                    + inputs["open_architecture_diagram"]
                    + textwrap.dedent(
                        """
                        ```
                        """
                    )
                ),
                (
                    textwrap.dedent(
                        """
                        ```json
                        """
                    )
                    + inputs["open_architecture_json_dump"]
                    + textwrap.dedent(
                        """
                        ```
                        """
                    )
                ),
            ]
        }


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
