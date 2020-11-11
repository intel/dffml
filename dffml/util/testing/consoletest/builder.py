"""
Sphinx builder used to run commands generated from parsed nodes
"""
import os
import sys
import time
import asyncio
import traceback
import contextlib
from typing import Dict, Any


from .runner import run_nodes


class BaseConsoleTestBuilder:
    name = "consoletest"

    def init(self) -> None:
        self.total_failures = 0
        self.total_tries = 0

        date = time.strftime("%Y-%m-%d %H:%M:%S")

        self.outfile = open(
            os.path.join(self.outdir, "output.txt"), "w", encoding="utf-8"
        )
        self.outfile.write(
            (
                "Results of %s builder run on %s\n"
                "===========%s================%s\n"
            )
            % (self.name, date, "=" * len(self.name), "=" * len(date))
        )

        if not os.path.isdir(self.config.consoletest_root):
            raise ValueError(
                "consoletest_root(%r) is not set or is not a valid directory"
                % (self.config.consoletest_root,)
            )
        if not os.path.isdir(self.config.consoletest_docs):
            raise ValueError(
                "consoletest_docs(%r) is not set or is not a valid directory"
                % (self.config.consoletest_docs,)
            )

        self.consoletest_test_setup = None
        if self.config.consoletest_test_setup:
            consoletest_test_setup = compile(
                self.config.consoletest_test_setup,
                "<consoletest_test_setup>",
                "exec",
                flags=0,
                dont_inherit=False,
                optimize=-1,
            )
            local_variables = {}
            exec(consoletest_test_setup, local_variables, local_variables)
            self.consoletest_test_setup = local_variables["setup"]

    def finish(self) -> None:
        # write executive summary
        def s(v: int) -> str:
            return "s" if v != 1 else ""

        repl = (
            self.total_tries,
            s(self.total_tries),
            self.total_failures,
            s(self.total_failures),
        )
        self._out(
            f"""
{self.name} summary
{"=" * len(self.name)}========
%5d test%s
%5d failure%s in tests
"""
            % repl
        )
        self.outfile.close()

        if self.total_failures:
            self.app.statuscode = 1

    @staticmethod
    def condition(node) -> bool:
        return (
            isinstance(node, (nodes.literal_block, nodes.comment))
            and "consoletestnodetype" in node
        )

    def test_doc(self, docname: str, doctree) -> None:
        # Get all applicable nodes
        doc_nodes = list(doctree.traverse(self.condition))

        if not doc_nodes:
            return

        print()
        print(f"{self.name} testing: {docname}")
        print()

        self.total_tries += 1

        watcher = asyncio.get_child_watcher()
        loop = asyncio.new_event_loop()
        watcher.attach_loop(loop)

        def cleanup():
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()

        # The stack that holds the temporary directories which contain the
        # current working directory must be unwound *after*
        # loop.shutdown_asyncgens() is called. This is to ensure that if any of
        # the generators use those directories, they still have access to them
        # (pdxjohnny) I'm not entirely sure if the above statement is true. I
        # was testing the shutdown of the HTTP server interacting with the model
        # directory and it didn't seem to work if I remember correctly.
        with contextlib.ExitStack() as stack:
            try:
                loop.run_until_complete(
                    run_nodes(
                        self.config.consoletest_root,
                        self.config.consoletest_docs,
                        stack,
                        doc_nodes,
                        setup=self.consoletest_test_setup,
                    )
                )
                cleanup()
            except:
                cleanup()
                self.total_failures += 1
                traceback.print_exc(file=sys.stderr)

        print()
        print("No more tempdir")
        print()


with contextlib.suppress(ModuleNotFoundError):
    from docutils import nodes
    from docutils.nodes import Node
    from docutils.parsers.rst import directives

    import sphinx
    from sphinx.locale import __
    from sphinx.ext.doctest import DocTestBuilder

    class ConsoleTestBuilder(BaseConsoleTestBuilder, DocTestBuilder):
        epilog = __(
            "Testing of consoletests in the sources finished, look at the "
            "results in %(outdir)s/output.txt."
        )


def setup(app: "Sphinx") -> Dict[str, Any]:
    app.add_builder(ConsoleTestBuilder)
    app.add_config_value("consoletest_root", "", False)
    app.add_config_value("consoletest_docs", "", False)
    app.add_config_value("consoletest_test_setup", "", False)
    return {"version": "0.0.1", "parallel_read_safe": True}
