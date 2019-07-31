# Hacking on DFFML

Install in development mode via pip.

```console
git clone https://github.com/intel/dffml
cd dffml
pip install --user -e .
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

```console
python3.7 setup.py test
```

# Check the Report for Unit Test Coverage

These commands will generate a folder `htmlcov`, you can check the report by
opening the `index.html` in a web browser.

```console
coverage run setup.py test
coverage report
coverage html
```

# Working on skel/

If you want to work on any of the packages in `skel/`, you'll need to run the
`skel link` command first fromt he `dev` service. This will symlink required
files in from `common/` so that testing will work.

```console
dffml service dev skel link
```
