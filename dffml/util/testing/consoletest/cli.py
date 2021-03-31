import sys
import json
import pathlib
import argparse
import contextlib
import dataclasses
from typing import List

from .parser import parse_nodes, Node
from .runner import run_nodes
from .util import code_block_to_dict, literalinclude_to_dict


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Node):
            return dataclasses.asdict(obj)
        return json.JSONEncoder.default(self, obj)


async def main(argv: List[str]) -> None:
    """
    Run consoletest on the file provided
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "infile", type=argparse.FileType("r", encoding="UTF-8")
    )
    parser.add_argument(
        "--parse",
        action="store_true",
        default=False,
        help="Dump parsed nodes as JSON and exit without running",
    )
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path(""))
    parser.add_argument("--docs", type=pathlib.Path, default=pathlib.Path(""))
    parser.add_argument("--setup", type=pathlib.Path, default=pathlib.Path(""))
    args = parser.parse_args(argv)

    if args.root == pathlib.Path(""):
        args.root = pathlib.Path(args.infile.name).parent
    if args.docs == pathlib.Path(""):
        args.docs = pathlib.Path(args.infile.name).parent

    if args.setup == pathlib.Path(""):
        args.setup = None
    else:
        args.setup = compile(
            args.setup.read_text(),
            "<setup>",
            "exec",
            flags=0,
            dont_inherit=False,
            optimize=-1,
        )
        local_variables = {}
        exec(args.setup, local_variables, local_variables)
        args.setup = local_variables["setup"]

    nodes = list(parse_nodes(args.infile.read()))

    if args.parse:
        print(json.dumps(nodes, indent=4, sort_keys=True, cls=JSONEncoder))
        return

    for node in nodes:
        if not node.options.get("test", False):
            continue
        if node.directive == "code-block":
            nodes.append(
                code_block_to_dict(node.content, node.options, node=node.node)
            )
        elif node.directive == "literalinclude":
            nodes.append(
                literalinclude_to_dict(node.content, node.options, node.node)
            )

    with contextlib.ExitStack() as stack:
        await run_nodes(args.root, args.docs, stack, nodes, setup=args.setup)

    args.infile.close()
