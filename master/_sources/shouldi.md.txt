# shouldi

![shouldi](https://github.com/intel/dffml/raw/master/examples/shouldi/shouldi.jpg)

## What Is ShouldI?

`shouldi` is a tool that runs static analysis tools to let you know if there are
any issues in any of the python packages you were thinking of installing.

`shouldi` is similar to things like [Go Report Card](https://goreportcard.com/).

> `shouldi` is in its very early stages. Expect things to change.

## Installation

```console
$ python3 -m pip install -U shouldi
```

## Usage

There are several different subcommands of `shoudli`

- [install](#install-command)
  - Analogous to `pip install` but runs checks to tell you if you should install
- [use](#use-command)
  - Point this command at any Git URL or directory and it will run appropriate
    static analysis tools for that language
- [project](#project-command)
  - Auto discover projects and dependencies of those projects within a directory

### Install Command

Run bandit and safety. Tell the person who ran the command not to install the
Python package if there were any issues found by either tool.

```console
$ shouldi install insecure-package bandit
bandit is okay to install
Do not install insecure-package! {'safety_check_number_of_issues': 1}
```

### Use Command

Given a Git URL or a directory, figure out what the language the codebase is and
run the appropriate static analysis tools for that language.

Tools for each language are as follows.

**You must have the following tools installed on the system**

- golang
  - [golangci-lint](https://github.com/golangci/golangci-lint/blob/master/README.md)
- java
  - [dependency-check](https://owasp.org/www-project-dependency-check/)
- javascript
  - [npm-audit](https://docs.npmjs.com/cli/audit)
- python
  - [safety](https://pyup.io/safety/)
  - [bandit](https://pypi.org/project/bandit/)
- rust
  - [cargo-audit](https://github.com/RustSec/cargo-audit)

```console
$ shouldi use https://github.com/trekhleb/javascript-algorithms
{'static_analysis': SAResultsSpec(critical=1, high=2941, medium=16, low=41049, report={'npm_audit_output': {'info': 0, 'low': 41049, 'moderate': 16, 'high': 2941, 'critical': 1}})}
```

### Project Command

Given a directory, output a JSON describing the dependencies found within that
directory.

At the moment it will auto discover Python dependencies listed in `setup.py`'s
`install_requires` section or within `requirements.txt`

Dependencies which cannot be automatically identified can be specified in YAML
files.

```yaml
dependencies:
  python:
    name: Python
    url: https://python.org
    license: Python License 2.0
```

Here's an example of running the project command on the `shouldi` codebase with
the above `deps.yaml` adding in dependencies that couldn't be auto discovered.

```console
$ shouldi project create -add deps.yaml -- .
{
    "dependencies": [
        {
            "extra": {
                "pypi": {
                    "euuid": "7bd67f47-9972-57fd-8da1-233783b35321",
                    "license": "Apache 2",
                    "name": "aiohttp",
                    "url": "https://pypi.org/pypi/aiohttp",
                    "uuid": null
                }
            },
            "license": "Apache 2",
            "name": "aiohttp",
            "url": "https://github.com/aio-libs/aiohttp",
            "uuid": "a6172a74-11ca-5624-bbf4-2e064084ee95"
        },
        {
            "extra": {
                "pypi": {
                    "euuid": "8ce644e4-20ef-5a24-85bb-0449fb8e2c94",
                    "license": "",
                    "name": "bandit",
                    "url": "https://pypi.org/pypi/bandit",
                    "uuid": null
                }
            },
            "license": null,
            "name": "bandit",
            "url": "https://bandit.readthedocs.io/en/latest/",
            "uuid": "1fa385fc-91ae-59c5-8d4c-220b9820f173"
        },
        {
            "extra": {
                "pypi": {
                    "euuid": "c09eaab1-7676-55b8-96fd-cb50f5dc125c",
                    "license": "MIT license",
                    "name": "safety",
                    "url": "https://pypi.org/pypi/safety",
                    "uuid": null
                }
            },
            "license": "MIT license",
            "name": "safety",
            "url": "https://github.com/pyupio/safety",
            "uuid": "f2cc3711-8652-584d-8d46-7e060398eff4"
        },
        {
            "extra": {
                "pypi": {
                    "euuid": "5143b2bf-be54-5688-8077-efbd038fbdc5",
                    "license": "MIT",
                    "name": "PyYAML",
                    "url": "https://pypi.org/pypi/PyYAML",
                    "uuid": null
                }
            },
            "license": "MIT",
            "name": "PyYAML",
            "url": "https://github.com/yaml/pyyaml",
            "uuid": "406495d7-1ba9-5a7e-bec9-f2a1119d3913"
        },
        {
            "extra": {},
            "license": "Python License 2.0",
            "name": "Python",
            "url": "https://python.org",
            "uuid": "807b7876-01ec-5fef-ad5a-4cc588b97719"
        },
    ]
}
```

## License

shouldi is distributed under the [MIT License](https://spdx.org/licenses/MIT.html).

#### What's This Really Called

The real name of this package is "DFFML Evaluator for PyPi Packages". `shouldi`
is merely the command line invocation, and we claim `shouldi`, the package name
on PyPi, to avoid a supply chain attack.
