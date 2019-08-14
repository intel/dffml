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

# Hacking on DFFML

Install in development mode via pip.

```console
git clone https://github.com/intel/dffml
cd dffml
pip install --user -e .[dev]
```

If you are working on Git features or Tensorflow models, `cd` into those
directories and do the same.

```console
cd model/tensorflow
pip install --user -e .
cd -
cd feature/git
pip install --user -e .
```

## File Formatting

- Run the [black](https://github.com/python/black) formatter on all files.
- There shall be no trailing whitespace
- Files should stick to 80 column width unless there is some programmatic
  constraint

```console
black dffml tests examples
```
# Git

Be sure to checkout a new branch to do your work on.

```console
git checkout origin/master
git pull
git checkout -b my_new_thing origin/master
```

You'll need to fork the repo on GitHub too. Then add that as a remote.

```console
# $USER in this case would be your github username
git remote add $USER git@github.com:$USER/dffml
```

Once you've committed a change on that branch you can push it to your fork.

```console
git push -u $USER my_new_thing
```

Then you can keep committing on this branch and just use `git push` to send your
new commits to GitHub.

# Testing

To get the debug output while testing:

```console
export LOGGING=debug
```

To run the tests:

```console
python3.7 setup.py test
```

## Test Coverage

- Each pull request is expected to maintain or increase coverage.

```console
coverage run setup.py test
coverage report -m
coverage html
```
# Check the Report for Unit Test Coverage

These commands will generate a folder `htmlcov`, you can check the report by
opening the `index.html` in a web browser.

```console
coverage run setup.py test
coverage report
coverage html
```
To view the coverage report at http://127.0.0.1:8080/.

```console
python3.7 -m http.server --directory htmlcov/ 8080
```


# Working on skel/

If you want to work on any of the packages in `skel/`, you'll need to run the
`skel link` command first fromt he `dev` service. This will symlink required
files in from `common/` so that testing will work.

```console
dffml service dev skel link
```
## Changelog

- Most PRs should include a description of what is changing to the
  [CHANGELOG.md](CHANGELOG.md) file. Use your own judgement on what warrants
  inclusion, the expectation is that 95% of PRs will include an edit to the
  change log. Maintainers will let you know if you need to include it or its not
  needed.

# Documentation

To build and view the documentation run the docs script.

```console
rm -rf pages/
./scripts/docs.sh
python3.7 -m http.server --directory pages/ 7000
```

## Community

- [Gitter Chat](https://gitter.im/dffml/community)
- [Weekly Meetings](https://intel.github.io/dffml/community.html)
- Mailing List [dffml-dev@lists.01.org](mailto:dffml-dev@lists.01.org)
  - https://lists.01.org/mailman/listinfo/dffml-dev
