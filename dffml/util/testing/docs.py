import io
import doctest
import inspect
import pathlib
import contextlib
from typing import Dict, Any, Optional, Union, List

from .consoletest.parser import parse_nodes
from .consoletest.runner import run_nodes
from .consoletest.commands import ConsoletestCommand
from .consoletest.util import (
    code_block_to_dict,
    literalinclude_to_dict,
    nodes_to_test,
)


def run_doctest(obj, state: Dict[str, Any] = None, check: bool = True):
    """
    Run doctest on the object provided. Globals should be passed via the
    ``globs`` key within the ``state`` dict. Globals are a key value mapping of
    the name of the global to the object it will be.

    You probably want to use state like so

    .. code-block:: python

        run_doctest(func, state={"globs": globals()})
    """
    if state is None:
        state = {}
    state.setdefault("verbose", False)
    state.setdefault("globs", {})

    finder = doctest.DocTestFinder(verbose=state["verbose"], recurse=False)
    runner = doctest.DocTestRunner(verbose=state["verbose"])

    for test in finder.find(obj, obj.__qualname__, globs=state["globs"]):
        output = io.StringIO()
        results = runner.run(test, out=output.write)
        if results.failed and check:
            raise Exception(output.getvalue())


async def run_consoletest(
    obj: Any,
    *,
    repo_root_dir: Optional[Union[str, pathlib.Path]] = None,
    docs_root_dir: Optional[Union[str, pathlib.Path]] = None,
    setup: Optional[List[ConsoletestCommand]] = None,
) -> None:
    """
    Run consoletest on the object provided.
    """
    if repo_root_dir is None:
        repo_root_dir = pathlib.Path(inspect.getsourcefile(obj)).parent
        while repo_root_dir != repo_root_dir.parent and (
            not (repo_root_dir / ".git").is_dir()
            or not (repo_root_dir / "setup.py").is_file()
        ):
            repo_root_dir = repo_root_dir.parent
    if docs_root_dir is None:
        docs_root_dir = pathlib.Path(inspect.getsourcefile(obj)).parent
    # Failsafe for if we traversed up all the way to the root of the filesystem
    # for the repo root dir.
    if repo_root_dir == repo_root_dir.parent:
        repo_root_dir = docs_root_dir

    with contextlib.ExitStack() as stack:
        await run_nodes(
            repo_root_dir,
            docs_root_dir,
            stack,
            nodes_to_test(parse_nodes(inspect.getdoc(obj))),
            setup=setup,
        )
