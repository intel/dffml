import os
import io
import pathlib
import tempfile
import contextlib
from typing import Union, List, Dict, Any, Optional

from .commands import ConsoletestCommand, ConsoleCommand, call_replace
from .util import copyfile


async def run_nodes(
    repo_root_dir: Union[str, pathlib.Path],
    docs_root_dir: Union[str, pathlib.Path],
    stack: contextlib.ExitStack,
    nodes: List[Dict[str, Any]],
    *,
    setup: Optional[List[ConsoletestCommand]] = None,
) -> None:
    # Ensure pathlib objects
    repo_root_dir = pathlib.Path(repo_root_dir)
    docs_root_dir = pathlib.Path(docs_root_dir)
    # Create an async exit stack
    async with contextlib.AsyncExitStack() as astack:
        tempdir = stack.enter_context(tempfile.TemporaryDirectory())

        ctx = {
            "root": str(repo_root_dir),
            "docs": str(docs_root_dir),
            "cwd": tempdir,
            "stack": stack,
            "astack": astack,
            "daemons": {},
            # Items in this context that must are not serializable
            "no_serialize": {"stack", "astack", "daemons"},
        }

        # Create a virtualenv for every document
        if setup is not None:
            await setup(ctx)

        for node in nodes:  # type: Element
            if node["consoletestnodetype"] == "consoletest-literalinclude":
                lines = node.get("lines", None)
                if lines is not None:
                    lines = tuple(map(int, lines.split("-")))

                # Handle navigating out of the docs_root_dir
                if node["source"].startswith("/.."):
                    node["source"] = node["source"][1:]

                src = os.path.join(str(docs_root_dir), node["source"])
                dst = os.path.join(ctx["cwd"], *node["filepath"])

                print()
                print("Copying", ctx, src, dst, lines)

                copyfile(src, dst, lines=lines)
                print(pathlib.Path(dst).read_text(), end="")
                print()
            elif node["consoletestnodetype"] == "consoletest-file":
                print()
                filepath = pathlib.Path(ctx["cwd"], *node["filepath"])

                if not filepath.parent.is_dir():
                    filepath.parent.mkdir(parents=True)

                if node["overwrite"] and filepath.is_file():
                    print("Overwriting", ctx, filepath)
                    mode = "wt"
                else:
                    print("Writing", ctx, filepath)
                    mode = "at"

                with open(filepath, mode) as outfile:
                    outfile.seek(0, io.SEEK_END)
                    outfile.write("\n".join(node["content"]) + "\n")

                print(filepath.read_text(), end="")
                print()
            elif node["consoletestnodetype"] == "consoletest":
                if node["consoletest_commands_replace"] is not None:
                    for command, new_cmd in zip(
                        node["consoletest_commands"],
                        call_replace(
                            node["consoletest_commands_replace"],
                            list(
                                map(
                                    lambda command: command.cmd
                                    if isinstance(command, ConsoleCommand)
                                    else [],
                                    node["consoletest_commands"],
                                )
                            ),
                            ctx,
                        ),
                    ):
                        if isinstance(command, ConsoleCommand):
                            command.cmd = new_cmd
                for command in node["consoletest_commands"]:
                    print()
                    print("Running", ctx, command)
                    print()
                    await astack.enter_async_context(command)
                    await command.run(ctx)
