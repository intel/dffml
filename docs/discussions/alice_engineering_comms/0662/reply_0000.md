- https://github.com/intel/cve-bin-tool/pull/4200
  - Merged!
    - 🛤️🛤️🛤️🛤️🛤️🛤️🛤️
- https://github.com/intel/cve-bin-tool/pull/4207

```python
class EntryPoint(importlib.metadata.EntryPoint):
    def load(self):
        module = importlib.import_module(self.value.split(":", maxsplit=1)[0])
        for name, cls in inspect.getmembers(module, predicate=inspect.isclass):
            if issubclass(cls, Checker) and cls is not Checker:
                return cls
        raise ImportError(
            f"Could not find a class deriving from cve_bin_tool.checkers.Checker in module: {module!r}"
        )
```

- TODO
  - [x] https://github.com/intel/cve-bin-tool/pull/4200
  - [ ] [![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/intel/dffml/badge)](https://scorecard.dev/viewer/?uri=github.com/intel/dffml)
    - [ ] https://github.com/intel/dffml/issues/1583
    - [x] `gh pr list --json url,author --jq '[.[] | select(.author.login == "app/dependabot")]`