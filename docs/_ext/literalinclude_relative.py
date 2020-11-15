"""
Override the literalinclude directive's read_file method so files not found from
docstrings of autodoc'd classes will be relative to the definition of the class.
"""
import pathlib
import inspect
import functools
from typing import List, Tuple, Dict, Any

from sphinx.config import Config
import sphinx.directives.code


def LiteralIncludeReader_read_file(func):
    @functools.wraps(func)
    def wrapper(
        self, filename: str, location: Tuple[str, int] = None
    ) -> List[str]:
        """
        Try to read the file, if it fails but we are looking at a docstring
        then try to read the file again but relative to the location of the file
        containing the docstring.
        """
        try:
            result = func(self, filename, location=location)
            return result
        except OSError:
            if (
                self.relative_filepath is None
                or location is None
                or "docstring of" not in location[0]
            ):
                raise

        docstring_location = pathlib.Path(location[0].split(":")[0]).parent

        filepath = (docstring_location / self.relative_filepath).resolve()

        return func(self, str(filepath), location=location)

    return wrapper


class LiteralIncludeReader(sphinx.directives.code.LiteralIncludeReader):
    def __init__(self, filename: str, options: Dict, config: Config) -> None:
        super().__init__(filename, options, config)
        # HACK Reach into caller's (LiteralInclude.run()) local variables and
        # access the self variable, which will have the arguements to
        # literalinclude, which is the unresolved relative path. Caller is the
        # first index in the list of FrameInfo objects returned by
        # inspect.stack()
        parent_locals = inspect.stack()[1].frame.f_locals
        if (
            "self" in parent_locals
            and hasattr(parent_locals["self"], "arguments")
            and isinstance(parent_locals["self"].arguments, (list, tuple))
            and parent_locals["self"].arguments
            and isinstance(parent_locals["self"].arguments[0], str)
        ):
            self.relative_filepath = pathlib.Path(
                *parent_locals["self"].arguments[0].split("/")
            )
        else:
            self.relative_filepath = None


sphinx.directives.code.LiteralIncludeReader = LiteralIncludeReader


LiteralIncludeReader.read_file = LiteralIncludeReader_read_file(
    LiteralIncludeReader.read_file
)


def setup(app: "Sphinx") -> Dict[str, Any]:
    return {"version": "0.0.1", "parallel_read_safe": True}
