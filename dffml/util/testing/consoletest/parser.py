import dataclasses
from typing import Dict, List, Union, Any


@dataclasses.dataclass
class Node:
    directive: str
    content: str
    options: Dict[str, Union[bool, str]]
    node: Dict[str, Any]


class ParseSingleNodeFailure(Exception):
    """
    Raised when a node could not be parsed
    """


class ParseNodesFailure(Exception):
    """
    Raised when text could not be parsed
    """


def get_indent(line) -> str:
    return line[: len(line) - len(line.lstrip())]


def remove_indent(lines: str) -> List[str]:
    # Find the lowest indentation level and remove it from all lines
    indents = list(
        map(
            lambda line: len(get_indent(line)),
            filter(lambda line: bool(line.strip()), lines),
        )
    )
    if not indents:
        return lines

    lowest_ident = min(indents)
    for i, line in enumerate(lines):
        lines[i] = line[lowest_ident:]

    return lines


def _parse_nodes(text: str) -> List[Node]:
    """
    Quick and dirty implementation of a .rst parser to extract directives
    """
    nodes = []

    c_indent = ""
    in_section = []
    directive = ""
    last_directive = ""
    args = ""
    last_args = ""
    text_split = text.split("\n")
    for i, line in enumerate(text_split):
        indent = get_indent(line)

        if line.strip().startswith(".. ") and "::" in line:
            last_directive = directive
            directive = line[line.index(".. ") + 3 : line.index("::")]
            if not last_directive:
                last_directive = directive
            last_args = args
            args = line[line.index("::") + 2 :]
            if not last_args:
                last_args = args
            if in_section:
                if not in_section[-1]:
                    in_section.pop()
                nodes.append((last_directive, last_args, in_section,))
            in_section = [""]
            c_indent = indent
        elif in_section:
            if len(indent) <= len(c_indent) and line.strip():
                if not in_section[-1]:
                    in_section.pop()
                nodes.append((directive, args, in_section,))
                if line.strip().startswith(".. ") and "::" in line:
                    last_directive = directive
                    directive = line[line.index(".. ") + 3 : line.index("::")]
                    if not last_directive:
                        last_directive = directive
                    last_args = args
                    args = line[line.index("::") + 2 :]
                    if not last_args:
                        last_args = args
                    in_section = [""]
                    c_indent = indent
                else:
                    in_section = []
                    c_indent = ""
            else:
                in_section.append(line)

    if in_section:
        if not in_section[-1]:
            in_section.pop()
        nodes.append((directive, args, in_section,))

    # Remove first blank line
    nodes = [
        (
            directive,
            list(map(lambda i: i.strip(), filter(bool, args.split()))),
            in_section[1:],
        )
        for directive, args, in_section in nodes
    ]

    new_nodes = []

    for directive, args, old_node in nodes:
        new_node = Node(directive=directive, options={}, content="", node={})
        option_lines = []

        try:
            if directive == "code-block":
                new_node.content = old_node[old_node.index("") + 1 :]
                option_lines = old_node[: old_node.index("")]
            elif directive == "literalinclude":
                option_lines = old_node
                new_node.node["source"] = args[0]

            # Parse the options
            if option_lines:
                option_lines = remove_indent(option_lines)
                for option in option_lines:
                    option_split = option.split(" ", maxsplit=1)
                    if len(option_split) == 1:
                        option_split.append(True)
                    new_node.options[option_split[0][1:-1]] = option_split[1]

            new_node.content = remove_indent(new_node.content)

        except Exception as error:
            raise ParseSingleNodeFailure(
                f"Failed to parse directive({directive}), args({args}), old_node: {old_node}"
            ) from error

        new_nodes.append(new_node)

    return new_nodes


def parse_nodes(text: str) -> List[Node]:
    try:
        return _parse_nodes(text)
    except Exception as error:
        raise ParseNodesFailure(f"Failed to parse: {text}") from error
