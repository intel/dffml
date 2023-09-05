## 2022-11-02 Harsh/John

- https://github.com/intel/dffml/issues/596#issuecomment-1301191994
- Installed VS Code build tools and used the developer prompt from there and it worked
- Remembered pipdeptree exists
- We should use https://github.com/tox-dev/pipdeptree and integrate that into shouldi.

```
  -j, --json            Display dependency tree as json. This will yield "raw"
                        output that may be used by external tools. This option
                        overrides all other options.
```

- https://intel.github.io/dffml/main/examples/shouldi.html
- https://intel.github.io/dffml/main/contributing/dev_env.html

```console
$ git clone https://github.com/intel/dffml
$ cd dffml
$ python -m venv .venv
$ git checkout -b deptree
$ . .venv/Scripts/activate
$ pip install -e .[dev]
$ cd examples/shouldi
$ pip install -e .[dev]
```

- https://intel.github.io/dffml/main/api/util/packaging.html#dffml.util.packaging.mkvenv
- https://github.com/tox-dev/pipdeptree#running-in-virtualenvs

https://github.com/intel/dffml/blob/b892cfab9bd152c47a709e8708491c95b8c3ec8e/tests/docs/test_consoletest.py#L14

- Basic testcase will be to analyze shouldi itself

https://github.com/intel/dffml/blob/3530ee0d20d1062605f82d1f5055f455f8c2c68f/dffml/util/testing/consoletest/commands.py#L83-L190

- Opens
  - Pip not installing to virtualenv we created (using different Python despite our current efforts)
- TODO
  - [ ] Harsh to investigate refactoring `ActivateVirtualEnvCommand` into something that doesn't mess with `os.environ` and behaves more like `mkvenv()` (https://github.com/intel/dffml/tree/main/dffml/util/testing/consoletest/)
    - [ ] Explicitly use path returned from venv creation as zeroith argument to `dffml.run_command()/subprocess.check_call()`