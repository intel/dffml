# Contributing

## Issue and Pull Request title formatting

Please create issues and Pull Requests with titles in the format of

`sub_module: file: Short description`

Since DFFML is organized mostly in a two level fashion, this will help us track
where changes are needed or being made at a glance.

Where the filename is the same as the directory name, this is the case with
Abstract Base classes, then omit the filename.

Here are some examples:

- `source: csv: Parse error due to seperator`
- `feature: Add abstract method new_method`
- `util: entrypoint: Change load_multiple`

## File Formatting

- Run the [black](https://github.com/python/black) formatter on all files.
- There shall be no trailing whitespace
- Files should stick to 80 column width unless there is some programmatic
  constraint

```console
black dffml tests examples
```

## Test Coverage

- Each pull request is expected to maintain or increase coverage.

```console
coverage run setup.py test
coverage report -m
coverage html
```

To view the coverage report at http://127.0.0.1:8080/.

```console
python3.7 -m http.server --directory htmlcov/ 8080
```

## Changelog

- Most PRs should include a description of what is changing to the
  [CHANGELOG.md](CHANGELOG.md) file. Use your own judgement on what warrants
  inclusion, the expectation is that 95% of PRs will include an edit to the
  change log. Maintainers will let you know if you need to include it or its not
  needed.

## Community

- Join the [Community](https://intel.github.io/dffml/community.html). Ask questions, share ideas, request features and what not.
- Join our [gitter](https://gitter.im/dffml/community) room and say Hi!
