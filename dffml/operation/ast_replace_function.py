"""
Replace python functions which might be problematic
"""
import ast
import sys
import copy
import argparse
import textwrap
import unittest


def recursive_replace_function(parent, i, obj, name, new_function_ast):
    if (
        isinstance(obj, (ast.FunctionDef, ast.AsyncFunctionDef))
        and obj.name == name
    ):
        parent[i] = new_function_ast
    elif isinstance(obj, list):
        for j, node in enumerate(obj):
            recursive_replace_function(obj, j, node, name, new_function_ast)
    elif hasattr(obj, "body") and isinstance(obj.body, list):
        recursive_replace_function(
            None, None, obj.body, name, new_function_ast
        )


def replace_function(old_code, funtion_name, new_function):
    old_code_ast = ast.parse(old_code)
    new_function_ast = ast.parse(new_function)
    new_code_ast = copy.deepcopy(old_code_ast)
    recursive_replace_function(
        None, None, new_code_ast, funtion_name, new_function_ast
    )
    # ast.unparse requires Python 3.9
    return ast.unparse(new_code_ast)


def make_parser():
    parser = argparse.ArgumentParser(prog="ast_replace_function.py")
    parser.add_argument("-n", "--name", help="Name of function to replace")
    parser.add_argument(
        "-f", "--func", type=argparse.FileType("r"), default=sys.stdin
    )
    parser.add_argument("-i", "--input", type=argparse.FileType("r"))
    parser.add_argument(
        "-o", "--output", type=argparse.FileType("w"), default=sys.stdout
    )
    return parser


def main():
    parser = make_parser()
    args = parser.parse_args()

    args.output.write(
        replace_function(args.input.read(), args.name, args.func.read()) + "\n"
    )


class TestReplaceFunction(unittest.TestCase):
    def test_replace_function(self):
        self.assertEqual(
            replace_function(
                textwrap.dedent(
                    """\
                    def main():
                        print('feedface')

                    main()
                    """
                ),
                "main",
                textwrap.dedent(
                    """\
                    def main():
                        print('deadbeaf')
                    """
                ),
            ),
            textwrap.dedent(
                """\
                def main():
                    print('deadbeaf')
                main()
                """
            ).rstrip(),
        )


if __name__ == "__main__":
    main()
