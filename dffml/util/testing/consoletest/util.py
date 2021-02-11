"""
Used to test ``code-block:: console`` portions of Sphinx documentation.
"""
import os
import io
import codecs
import shutil
import pathlib
import contextlib
from typing import (
    Any,
    Dict,
    List,
    Union,
    Tuple,
    Optional,
)

from .parser import Node
from .commands import build_command, parse_commands


@contextlib.contextmanager
def chdir(new_path):
    """
    Context manager to change directroy
    """
    old_path = os.getcwd()
    os.chdir(new_path)
    try:
        yield
    finally:
        os.chdir(old_path)


def copyfile(
    src: str, dst: str, *, lines: Optional[Union[int, Tuple[int, int]]] = None
) -> None:
    dst_path = pathlib.Path(dst)
    if not dst_path.parent.is_dir():
        dst_path.parent.mkdir(parents=True)

    if not lines:
        shutil.copyfile(src, dst)
        return

    with open(src, "rt") as infile, open(dst, "at") as outfile:
        outfile.seek(0, io.SEEK_END)
        for i, line in enumerate(infile):
            # Line numbers start at 1
            i += 1
            if len(lines) == 1 and i == lines[0]:
                outfile.write(line)
                break
            elif i >= lines[0] and i <= lines[1]:
                outfile.write(line)
            elif i > lines[1]:
                break


def literalinclude_to_dict(
    content: List[str],
    options: Dict[str, Union[bool, str]],
    node: Dict[str, Any],
) -> Dict[str, Any]:
    if node is None:
        node = {}

    if "source" not in node:
        raise ValueError('node must have "source" property')

    if "test" in options:
        node["consoletestnodetype"] = "consoletest-literalinclude"
        node["lines"] = options.get("lines", None)
        node["filepath"] = options.get(
            "filepath", os.path.basename(node["source"])
        ).split("/")

    return node


LITERALINCLUDE_OPTION_SPEC = {"filepath": "unchanged_required", "test": "flag"}


def code_block_to_dict(
    content: List[str],
    options: Dict[str, Union[bool, str]],
    *,
    node: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if node is None:
        node = {}

    if "filepath" in options:
        node["consoletestnodetype"] = "consoletest-file"
        node["content"] = content
        node["filepath"] = options["filepath"].split("/")
        node["overwrite"] = bool("overwrite" in options)
    elif "test" in options:
        node.setdefault("language", "console")
        node["consoletestnodetype"] = "consoletest"
        node["consoletest_commands"] = list(
            map(build_command, parse_commands(content))
        )

        node["consoletest_commands_replace"] = options.get("replace", None)
        for command in node["consoletest_commands"]:
            command.poll_until = bool("poll-until" in options)
            command.compare_output = options.get("compare-output", None)
            command.compare_output_imports = options.get(
                "compare-output-imports", None
            )
            if command.poll_until and command.compare_output is None:
                raise ValueError(
                    "Cannot set poll-until without compare-output"
                )
            command.ignore_errors = bool("ignore-errors" in options)
            if "stdin" in options:
                command.stdin = codecs.getdecoder("unicode_escape")(
                    options["stdin"]
                )[0]

        # Last command to be run is a daemon
        if "daemon" in options:
            node["consoletest_commands"][-1].daemon = options["daemon"]

    return node


CODE_BLOCK_OPTION_SPEC = {
    "filepath": "unchanged_required",
    "replace": "unchanged_required",
    "poll-until": "flag",
    "compare-output": "unchanged_required",
    "compare-output-imports": "unchanged_required",
    "ignore-errors": "flag",
    "daemon": "unchanged_required",
    "test": "flag",
    "stdin": "unchanged_required",
    "overwrite": "flag",
}


def nodes_to_test(nodes: List[Node]) -> List[Node]:
    """
    List of nodes to subset of that list which have the ``:test::`` option.
    """
    subset_nodes = []

    for node in nodes:
        if not node.options.get("test", False):
            continue
        if node.directive == "code-block":
            subset_nodes.append(
                code_block_to_dict(node.content, node.options, node=node.node)
            )
        elif node.directive == "literalinclude":
            subset_nodes.append(
                literalinclude_to_dict(node.content, node.options, node.node)
            )

    return subset_nodes
