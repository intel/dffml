# shouldi

![shouldi](https://github.com/intel/dffml/raw/master/examples/shouldi/shouldi.jpg)

## Usage

```console
$ shouldi install insecure-package bandit
bandit is okay to install
Do not install insecure-package! {'safety_check_number_of_issues': 1}
```

## Dependencies

`shouldi` depends on safety, pylint, and bandit being installed separately.

```console
$ python3.7 -m pip install -U safety pylint bandit
```

## WTF is this

`shouldi` is a tool that runs static analysis tools to let you know if there are
any issues in any of the python packages you were thinking of installing.

`shouldi` is similar to things like [Go Report Card](https://goreportcard.com/).

Right now `shouldi` runs the following static analysis tools and complains if:

- [safety](https://pyup.io/safety/)
  - Any issues are found
- TODO: [bandit](https://pypi.org/project/bandit/)
- TODO: [pylint](https://pypi.org/project/pylint/)
  - TDB (something about the number of errors)

## License

shouldi is distributed under the [MIT License](LICENSE).

#### What's This Really Called

The real name of this package is "DFFML Evaluator for PyPi Packages". `shouldi`
is mearly the command line invokation, and we claim `shouldi`, the package name
on PyPi, to avoid a supply chain attack.
