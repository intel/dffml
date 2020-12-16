# consoletest Sphinx extension

This Sphinx extension allows you to tests your `code-block` and
`literalinclude` directives in your documentation to make sure that the command
you're telling users to run, and the files you're telling them to write, produce
intended results.

- [Example](#example)

- [`conf.py`](#confpy)

- [Options](#options)

  - [`code-block`](#code-block)

  - [`literalinclude`](#literalinclude)

## Example

Each `.rst`, `.md`, .etc file will get it's own temporary directory in which the
test will run.

One "test" is the running of all directives in a file marked with the `:test:`
option.

We can run `consoletest` on a file by invoicing it as a Python module. We'll
test the following command in this document by running:

```console
$ python -m dffml.util.testing.consoletest dffml/util/testing/consoletest/README.md
```

Write out this `README.md` file into the temporary directory which is the
current working directory.

```rst
.. literalinclude:: README.md
    :test:
```

Start an HTTP server which will serve the content of the current working
directory. Mark the server as a daemon which will run in the background for the
remainder of the test of this document.

```rst
.. code-block:: console
    :test:
    :daemon: 9000

    $ python -m http.server 9000
```

`poll-until` means run the following command until the contents of the
Python code in the `compare-output` option evaluates to `True`. Ignore any
errors by specifying the `ignore-errors` option.

```rst
.. code-block:: console
    :test:
    :poll-until:
    :ignore-errors:
    :compare-output: bool(b":compare-output:" in stdout)

    $ curl -sfL http://localhost:9000/README.md
```

Declare that we want to replace the existing daemon labeled "9000" with this new
process. Terminate the previously running HTTP server by sending it a `Ctrl-C`.

```rst
.. code-block:: console
    :test:
    :daemon: 9000

    $ python -m http.server --cgi 9000
```

Commands should be placed on separate lines, `&&` and command substitution are
currently not supported.

```rst
.. code-block:: console
    :test:

    $ mkdir cgi-bin
    $ chmod 755 cgi-bin
    $ touch cgi-bin/api.py
```

Content of command can be replaced using the `:replace:` option. Usually you'll
want to use this if something you need in the example relies on a value within
the `ctx` dictionary.

```rst
.. code-block:: console
    :test:
    :replace: import os; cmds[-1][-1] = os.path.join(ctx["cwd"], cmds[-1][-1])

    $ ls -lAFR
    $ chmod 755 cgi-bin/api.py
```

Contents of `code-block` directives can also be written to files

```rst
.. code-block:: python
    :test:
    :filepath: cgi-bin/api.py

    #!/usr/bin/env python
    import os
    import sys
    import json
    import urllib.parse

    print("Content-Type: application/json")
    print()

    query = dict(urllib.parse.parse_qsl(os.getenv("QUERY_STRING", default="")))

    print(json.dumps(query))

    sys.stdout.flush()
```

Pipes are supported. The `stdin` option allows for specifying the input to a
command. String literals will be decoded, for example `\n` will become a
newline.

When running network clients such as `curl` against a server, you will sometimes
need to use `:poll-until:` and `:ignore-errors:` to re-run the client until the
server is ready to respond to requests.

```rst
.. code-block:: console
    :test:
    :stdin: http://localhost:9000/cgi-bin/api.py?Hello=World
    :poll-until:
    :ignore-errors:
    :compare-output-imports: json
    :compare-output: bool({"Hello": "World"} == json.loads(stdout.decode()))

    $ cat | xargs curl -vfL
```

### `conf.py`

If you install DFFML you will have `consoletest` installed. Simply add it to
your list of extensions using it's full path.

**conf.py**

```python
extensions = [
    ...
    "dffml.util.testing.consoletest.builder",
    ...
]
```

It needs to be configured by defining three variables.

- The path to the root of your git repo

- The path to the docs source

- If desired, Python code (as a `str`) containing an `async` function named
  `setup()` which will be run before each test.

**conf.py**

```python
consoletest_root = os.path.abspath("..")
consoletest_docs = os.path.join(consoletest_root, "docs")
consoletest_test_setup = (
    pathlib.Path(__file__).parent / "consoletest_test_setup.py"
).read_text()
```

Here is an example of `consoletest_test_setup.py` which resides in the same
directory as `conf.py` (per above configuration).

The `setup()` function in this example

- Creates a new virtual environment (a `conda` environment will be created if
  running within an activated `conda` environment already)

- Activates the virtual environment

- Installs the latest versions of `pip`, `setuptools`, and `wheel`

- Installs the package at the root of the git repo (`consoletest_root`) in
  development mode. This way each tests starts with an isolated environment
  containing the packages being tested already installed.

**consoletest_test_setup.py**

```python
import tempfile

from dffml.util.testing.consoletest.commands import (
    CreateVirtualEnvCommand,
    ActivateVirtualEnvCommand,
    PipInstallCommand,
)


async def setup(ctx):
    """
    Create a virtualenv for every document
    """
    venvdir = ctx["stack"].enter_context(tempfile.TemporaryDirectory())

    ctx["venv"] = venvdir

    for command in [
        CreateVirtualEnvCommand(ctx["venv"]),
        ActivateVirtualEnvCommand(ctx["venv"]),
        PipInstallCommand(
            [
                "python",
                "-m",
                "pip",
                "install",
                "-U",
                "pip",
                "setuptools",
                "wheel",
            ]
        ),
        PipInstallCommand(
            [
                "python",
                "-m",
                "pip",
                "install",
                "-U",
                "-e",
                ctx["root"],
            ]
        ),
    ]:
        print()
        print("[setup] Running", ctx, command)
        print()
        await ctx["astack"].enter_async_context(command)
        await command.run(ctx)
```

## Options

Multiple options have been added to the `code-block` and `literalinclude`
directives.

### `code-block`

- `test`: Boolean

  - Run this `code-block` as a part of the `consoletest`

- `filepath`: String

  - Write the contents of the `code-block` to this file path relative to the
    currnet working directory (`ctx["cwd"]`)

- `replace`: Python code

  - Replace parts of commands before they are run. Useful if a command needs
    access to something within the `ctx`.

  - Example: `:replace: cmds[0][-5] = cmds[0][-5].replace("8080", str(ctx["HTTP_SERVER"]["8080"]))`

- `poll-until`: Boolean

  - Run the command until `:compare-output:` evaluates to `True`.

- `ignore-errors`: Boolean

  - Do not fail the whole test if the command exits with a non-zero exit code.

- `compare-output-imports`: Comma seperated list of Python modules

  - Python modules to import before running `compare-output`

  - Example: `:compare-output-import: os, json`

- `compare-output`: Python code

  - Body of Python lambda used to check if output of command was as expected

  - Example: `:compare-output: bool(json.loads(stdout.decode()) == json.loads(os.environ['VAR']))`

- `daemon`: String

  - Do not wait for the command to finish before running the next command. Run
    the command in the background until the test run is over, or until another
    command is run with the same string given.

  - Example: `:daemon: my-background-process`

- `stdin`: String

  - Data to use as the processes input. String literals will be converted.
    For example `\n` becomes a new line.

  - Example: `Hello\nWorld`

### `literalinclude`

- `test`: Boolean

  - Copy the file referenced by this `literalinclude` into the current working
    directory (`ctx["cwd"]`) as a part of the `consoletest`.

- `filepath`: String

  - Write the contents of the file referenced by `literalinclude` to this file
    path relative to the current working directory (`ctx["cwd"]`).

    If this option is not given the basename of the file referenced by
    `literalinclude` will be used.
