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

# Check the Report for Unit Test Coverage

These commands will generate a folder `htmlcov`, you can check the report by
opening the `index.html` in a web browser.

```console
coverage run setup.py test
coverage report
coverage html
```

# Documentation

To build and view the documentation run the docs script.

```console
rm -rf pages/
./scripts/docs.sh
python3.7 -m http.server --directory pages/ 7000
```

# Working on skel/

If you want to work on any of the packages in `skel/`, you'll need to run the
`skel link` command first fromt he `dev` service. This will symlink required
files in from `common/` so that testing will work.

```console
dffml service dev skel link
```

# Debugging Entrypoint Issues

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
