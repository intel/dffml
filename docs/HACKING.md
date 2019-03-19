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
