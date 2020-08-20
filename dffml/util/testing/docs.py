import io
import doctest
from typing import Dict, Any


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
