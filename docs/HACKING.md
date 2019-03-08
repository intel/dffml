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

# Testing

```console
python3.7 setup.py test
```
