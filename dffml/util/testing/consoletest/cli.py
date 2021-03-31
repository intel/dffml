import sys
import pathlib
import argparse
import contextlib
from typing import List

from .parser import parse_nodes
from .runner import run_nodes
from .util import code_block_to_dict, literalinclude_to_dict


async def main(argv: List[str]) -> None:
    """
    Run consoletest on the file provided
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "infile", type=argparse.FileType("r", encoding="UTF-8")
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

    nodes = []

    for node in parse_nodes(args.infile.read()):
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
