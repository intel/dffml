# Contributing

Contributions can come in many forms, we always need help improving the
documentation. If you find issues with the documentation, usability, code, or
even a question, please open an
[issue](https://github.com/intel/dffml/issues/new/choose) to let us know.

- [Contacting the Community](#contacting-the-community)
- [What To Work On](#what-to-work-on)
- [Getting Set Up To Work On DFFML](#getting-set-up-to-work-on-dffml)
- [Working On A Branch](#working-on-a-branch)
- [File Formatting](#file-formatting)
- [Issue and Pull Request title formatting](#issue-and-pull-request-title-formatting)
- [Testing](#testing)
- [Documentation](#documentation)
- [Notes on Various Subsystems](#notes-on-various-subsystems)
- [Debugging](#debugging)

## Contacting the Community

You can get involved in DFFML via the following channels.

- [Gitter Chat](https://gitter.im/dffml/community)
- [Weekly Meetings](https://intel.github.io/dffml/community.html)
  - Recordings: https://www.youtube.com/channel/UCorEDRWGikwBH3dsJdDK1qA
- Open an [issue](https://github.com/intel/dffml/issues/new/choose)
- Users of DFFML Discussion Mailing List
  - Ask by emailing: [dffml-users@lists.01.org](mailto:dffml-users@lists.01.org)
  - Subscribe: https://lists.01.org/postorius/lists/dffml-users.lists.01.org/
- Development of DFFML Discussion Mailing List
  - Send emails to: [dffml-dev@lists.01.org](mailto:dffml-dev@lists.01.org)
  - Subscribe: https://lists.01.org/postorius/lists/dffml-dev.lists.01.org/

## What To Work On

GitHub issue labels will let you know what needs help and help you find a
project that fits your time budget. Thank you for your help!

- Estimated Time to Complete
  - tXS, tS, tM, tL, tXL
  - [XS: Extra Short](https://github.com/intel/dffml/labels/tXS)
    - Find and replace, fix a spelling mistake, make a change that shouldn't
      break anything.
  - [S: Short](https://github.com/intel/dffml/labels/tS)
    - Changes that are pretty much localized to one package
  - [M: Medium](https://github.com/intel/dffml/labels/tM)
    - Changes in one package that require changes in other packages
  - [L: Long](https://github.com/intel/dffml/labels/tL)
    - Changes to core architecture or functionality, API breaking changes
  - [XL: Extra Long](https://github.com/intel/dffml/labels/tXL)
    - Re-write the codebase(s) in another language

- Priority
  - [Nice To Have](https://github.com/intel/dffml/labels/p4)
  - [Average Priority](https://github.com/intel/dffml/labels/p3)
  - [Medium Priority](https://github.com/intel/dffml/labels/p2)
  - [High Priority](https://github.com/intel/dffml/labels/p1)
  - [Critical Priority](https://github.com/intel/dffml/labels/p0)
  - Scale of 0 to 4 with 0 being most critical and 4 being nice to have

### Who's Working On What

We all overcommit sometimes, here are the rules for how you can tell if you
should work on something, if someone else is already working on it, or if
someones work has been abandoned (they might not have time to tell us that they
don't have time to work on it anymore).

- Don't worry about asking if you can work on something.
- If you have started work on something but do not yet have a pull request
  - Comment saying you have started
  - If you don't open a draft/WIP pull request within 7 days, we will take that
    to mean you're not working on it anymore.
- If you see an open a draft/WIP pull request that hasn't had any activity on it
  for more than 21 days. The community should considered it abandoned.
  - If you are still working on it, comment on it saying so. It's okay to be in
    progress for a while, just make sure you let others know that you intend to
    complete it.
- If you see an abandoned pull request, you can work on the issue it is
  partaining to.
  - You must comment on the pull request to let others know that you intend to
    pick up the work.
  - You should consider picking up where the person left off by using the work
    they've posted.
    - Add a `Co-authored-by` tag to any of their commits that you change, and
      leave them as the author for any commits you don't change.

### Communication Style

Logs, screenshots, the command you were running, and any files involved make
it easier for other developers to replicate whatever happened so they can help
you fix the problem.

Even better than a screenshot is an
[asciicast](https://asciinema.org/docs/installation). It lets you create a
recording of your terminal that can be shared via a asciinema.org link or sent
privately as a JSON file.

Creating an issue and uploading any files or screenshots is always encouraged.

## Getting Set Up To Work On DFFML

To start contributing code to DFFML you'll need to download and install it in
development mode.

Before you install DFFML in development mode be sure to uninstall it! Python
will use the version installed from PyPi rather than you're development version
unless you uninstall it first!

```console
$ python3.7 -m pip uninstall dffml
```

Once you're sure DFFML is not installed on your system, install it in
development mode.

Installing to your home directory is the recommended installation method. To do
this we use the `--prefix=~/.local` flag.

> `pip` sometimes gets confused about the `--user` flag (and will blow up in
> your face if you try to pass it). So we use the `--prefix=~/.local` flag,
> which has the same effect but should always work.

```console
$ git clone https://github.com/intel/dffml
$ cd dffml
$ python3.7 -m pip install --prefix=~/.local -e .[dev]
```

> `[dev]` tells `pip` to install the dependencies you'll need to do development
> work on DFFML (such as documentation generation utilities).

Verify you can use `dffml` from the command line.

```console
$ dffml version
dffml version 0.3.1 (devmode: /wherever/you/cloned/dffml)
```

If you see `dffml` in `~/.local/bin` but you can't run it on the command line,
then you'll need to add that directory to your `PATH` environment variable.
This might need to be in `~/.bashrc`, `~/.bash_profile`, or `~/.profile`,
depending on your flavor of UNIX or Linux Distro.

```console
$ echo 'export PATH="${HOME}/.local/bin:${PATH}"' >> ~/.bashrc
$ source ~/.bashrc
```

If you are working on any of the plugins to DFFML maintained within it's
repository make sure to install those in development mode as well.

> For example, to install the TensorFlow models

```console
$ python3.7 -m pip install --prefix=~/.local -e model/tensorflow
```

To install all the plugins in development mode use the development service's
install command.

> To install to your home directory (`~/.local`), use the `-user` flag. Do NOT
> run install `-user` with `sudo`.

```console
$ dffml service dev install -user
```

## Working On A Branch

Be sure to checkout a new branch to do your work on.

```console
$ git fetch origin
$ git checkout -b my_new_thing origin/master
```

You'll need to fork the repo on GitHub too. Then add that as a remote.

> `$USER` in this case would be your GitHub username

```console
$ git remote add $USER git@github.com:$USER/dffml
```

Once you've committed a change on that branch you can push it to your fork.

```console
$ git push -u $USER my_new_thing
```

Then you can keep committing on this branch and just use `git push` to send your
new commits to GitHub.

## File Formatting

Run the [black](https://github.com/python/black) formatter on all files

```console
$ black .
```

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
- `model: tensorflow: Add XYZ classifier`

If you've already made the commit, you can change the message by amending the
commit.

```console
$ git commit --amend
```

## Testing

Run the tests with

```console
python3.7 setup.py test
```

To run a specific test, use the `-s` flag.

```console
python3.7 setup.py test -s tests.test_cli.TestPredict.test_repo
```

### Debug Logging

To get the debug output while testing set the `LOGGING` environment variable.

```console
export LOGGING=debug
```

### Test Coverage

Each pull request is expected to maintain or increase test coverage

```console
$ python3.7 -m coverage run setup.py test
$ python3.7 -m coverage report -m
$ python3.7 -m coverage html
```

The last command generates a folder called `htmlcov`, you can check the report
by opening the `index.html` in a web browser.

```console
python3.7 -m http.server --directory htmlcov/ 8080
```

You can now view the coverage report at http://127.0.0.1:8080/

### Test Datasets

In order to avoid potential legal issues, all datasets included within the
codebase of DFFML should be randomly generated.

## Documentation

To build and view the documentation run the docs script.

```console
$ rm -rf pages/
$ ./scripts/docs.sh
$ python3.7 -m http.server --directory pages/ 7000
```

## Notes on Various Subsystems

DFFML is comprised of various subsystems. The following are some notes
that might be helpful when working on each of them.

### Working on skel/

The packages in `skel/` are used to create new DFFML packages.

> For example, to create a new package containing operations.

```console
$ dffml service dev create operations dffml-operations-feedface
```

If you want to work on any of the packages in `skel/`, you'll need to run the
`skel link` command first fromt he `dev` service. This will symlink required
files in from `common/` so that testing will work.

```console
$ dffml service dev skel link
```

## Debugging

The following are ways to debug issues you might run into when working on DFFML.

Many times issues are because a package you are working on is not installed in
development mode. First try checking `~/.local/lib/python3.7/site-packages/` and
if you see anything other than `.egg-link` behind the name of the `dffml`
package you are working on, you probably need to delete that package and
re-install it in development mode (`pip install -e`).

### Plugin Loading / Entrypoint Issues

If you can't load the plugin you've been working on via the command line
interface, HTTP API, etc. It's probably an entry point issue.

The `dev` service has a helper command to help you debug issues with installed
entrypoints.

```console
$ dffml service dev entrypoints list dffml.model
tfdnnc = dffml_model_tensorflow.dnnc:DNNClassifierModel -> dffml-model-tensorflow 0.2.0 (/home/user/Documents/python/dffml/model/tensorflow)
scratchslr = dffml_model_scratch.slr:SLR -> dffml-model-scratch 0.0.1 (/home/user/Documents/python/dffml/model/scratch)
scikitadaboost = dffml_model_scikit.scikit_models:AdaBoostClassifierModel -> dffml-model-scikit 0.0.1 (/home/user/Documents/python/dffml/model/scikit)
scikitdtc = dffml_model_scikit.scikit_models:DecisionTreeClassifierModel -> dffml-model-scikit 0.0.1 (/home/user/Documents/python/dffml/model/scikit)
scikitgnb = dffml_model_scikit.scikit_models:GaussianNBModel -> dffml-model-scikit 0.0.1 (/home/user/Documents/python/dffml/model/scikit)
scikitgpc = dffml_model_scikit.scikit_models:GaussianProcessClassifierModel -> dffml-model-scikit 0.0.1 (/home/user/Documents/python/dffml/model/scikit)
scikitknn = dffml_model_scikit.scikit_models:KNeighborsClassifierModel -> dffml-model-scikit 0.0.1 (/home/user/Documents/python/dffml/model/scikit)
scikitlr = dffml_model_scikit.scikit_models:LinearRegressionModel -> dffml-model-scikit 0.0.1 (/home/user/Documents/python/dffml/model/scikit)
scikitmlp = dffml_model_scikit.scikit_models:MLPClassifierModel -> dffml-model-scikit 0.0.1 (/home/user/Documents/python/dffml/model/scikit)
scikitqda = dffml_model_scikit.scikit_models:QuadraticDiscriminantAnalysisModel -> dffml-model-scikit 0.0.1 (/home/user/Documents/python/dffml/model/scikit)
scikitrfc = dffml_model_scikit.scikit_models:RandomForestClassifierModel -> dffml-model-scikit 0.0.1 (/home/user/Documents/python/dffml/model/scikit)
scikitsvc = dffml_model_scikit.scikit_models:SVCModel -> dffml-model-scikit 0.0.1 (/home/user/Documents/python/dffml/model/scikit)
```
