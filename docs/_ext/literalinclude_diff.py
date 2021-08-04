"""
Override the literalinclude directive's show_diff method so we can override the
diff'd files paths
"""
import functools
from typing import List, Dict, Any

from docutils.nodes import Node
from docutils.parsers.rst import directives

from sphinx.directives.code import LiteralInclude, LiteralIncludeReader


def LiteralIncludeReader_show_diff(func):
    @functools.wraps(func)
    def wrapper(self) -> List[Node]:
        lines = func(self)

        if "diff-files" in self.options:
            # Grab the filepath(s) to use from the diff-files option
            old_path = self.options["diff-files"].split(" ", maxsplit=1)
            # Ensure paths start with ./ if not given
            for i, file_path in enumerate(old_path):
                if file_path.startswith("/") or file_path.startswith("./"):
                    continue
                old_path[i] = "./" + file_path
            # Check if we want to use the same filename for both, or different
            if len(old_path) == 2:
                new_path = old_path[1]
            else:
                new_path = old_path[0]
            old_path = old_path[0]
            # Perform the replacement
            lines[0] = f"--- {old_path}\n"
            lines[1] = f"+++ {new_path}\n"

        return lines

    return wrapper


# For fixing up diff paths
LiteralIncludeReader.show_diff = LiteralIncludeReader_show_diff(
    LiteralIncludeReader.show_diff
)
LiteralInclude.option_spec.update(
    {"diff-files": directives.unchanged_required}
)


def setup(app: "Sphinx") -> Dict[str, Any]:
    return {"version": "0.0.1", "parallel_read_safe": True}
