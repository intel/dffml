"""
Monkey patch the literalinclude and code-block directives to add new options to
them specific to consoletest.
"""
import functools
import contextlib
from typing import List

from .util import (
    LITERALINCLUDE_OPTION_SPEC,
    literalinclude_to_dict,
    CODE_BLOCK_OPTION_SPEC,
    code_block_to_dict,
)


def LiteralInclude_run(func):
    @functools.wraps(func)
    def wrapper(self) -> List[Node]:
        return [
            literalinclude_to_dict(self.content, self.options, func(self)[0])
        ]

    return wrapper


def CodeBlock_run(func):
    @functools.wraps(func)
    def wrapper(self) -> List[Node]:
        return [
            code_block_to_dict(self.content, self.options, node=func(self)[0])
        ]

    return wrapper


# Try to override the code-block directive's run method so we can pick up the
# flags we've added if docutils and sphinx are installed
with contextlib.suppress(ModuleNotFoundError):
    from docutils.nodes import Node
    from docutils.parsers.rst import directives

    import sphinx
    from sphinx.directives.code import LiteralInclude, CodeBlock

    LiteralInclude.run = LiteralInclude_run(LiteralInclude.run)
    LiteralInclude.option_spec.update(
        {
            key: getattr(directives, value)
            for key, value in LITERALINCLUDE_OPTION_SPEC.items()
        }
    )

    CodeBlock.run = CodeBlock_run(CodeBlock.run)
    CodeBlock.option_spec.update(
        {
            key: getattr(directives, value)
            for key, value in CODE_BLOCK_OPTION_SPEC.items()
        }
    )
