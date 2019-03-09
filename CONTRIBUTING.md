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

- There shall be no trailing whitespace
- Files should stick to 80 column width unless there is some programmatic
  constraint

## Changelog

- Most PRs should include a description of what is changing to the
  [CHANGELOG.md](CHANGELOG.md) file. Use your own judgement on what warrants
  inclusion, the expectation is that 95% of PRs will include an edit to the
  change log. Maintainers will let you know if you if you include and its not
  needed.
