## Troubleshooting Failed `pip install` Commands

### Context

Sometimes downloading a package with pip will fail.

```console
$ ulimit -c unlimited
$ python -m pip download torch
Collecting torch
  Downloading torch-1.12.1-cp39-cp39-manylinux1_x86_64.whl (776.4 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╸ 776.3/776.4 MB 13.0 MB/s eta 0:00:01Killed
```

### Possible Solution: Manual Install of Problematic Python Dependency

- This troubleshooting solution covers
  - Increase memory limit for processes (userspace)
  - Find the download URL of a python package
  - Download a python package with download resumption
  - Verify the contents of the package downloaded using a SHA
  - Install package from downloaded wheel

Look for the path to the download you want.

```console
$ curl -sfL https://pypi.org/simple/torch/ | grep torch-1.12.1-cp39-cp39-manylinux1_x86_64.whl
    <a href="https://files.pythonhosted.org/packages/1e/2f/06d30fbc76707f14641fe737f0715f601243e039d676be487d0340559c86/torch-1.12.1-cp39-cp39-manylinux1_x86_64.whl#sha256=9b356aea223772cd754edb4d9ecf2a025909b8615a7668ac7d5130f86e7ec421" data-requires-python="&gt;=3.7.0" >torch-1.12.1-cp39-cp39-manylinux1_x86_64.whl</a><br />
```

Download the package.

```console
$ curl -fLOC - https://files.pythonhosted.org/packages/1e/2f/06d30fbc76707f14641fe737f0715f601243e039d676be487d0340559c86/torch-1.12.1-cp39-cp39-manylinux1_x86_64.whl
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  740M  100  740M    0     0  85.1M      0  0:00:08  0:00:08 --:--:--  106M
```

Verify the SHA appended to our downloaded URL from our initial command.

```console
$ sha256sum -c - <<<'9b356aea223772cd754edb4d9ecf2a025909b8615a7668ac7d5130f86e7ec421  torch-1.12.1-cp39-cp39-manylinux1_x86_64.whl'
torch-1.12.1-cp39-cp39-manylinux1_x86_64.whl: OK
```

Update the package manager

```console
$ python -m pip install -U pip setuptools wheel
Defaulting to user installation because normal site-packages is not writeable
Requirement already satisfied: pip in /.pyenv/versions/3.9.13/lib/python3.9/site-packages (22.2.1)
Collecting pip
  Downloading pip-22.2.2-py3-none-any.whl (2.0 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.0/2.0 MB 10.3 MB/s eta 0:00:00
Requirement already satisfied: setuptools in /.pyenv/versions/3.9.13/lib/python3.9/site-packages (63.2.0)
Collecting setuptools
  Downloading setuptools-65.3.0-py3-none-any.whl (1.2 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.2/1.2 MB 16.5 MB/s eta 0:00:00
Requirement already satisfied: wheel in /.pyenv/versions/3.9.13/lib/python3.9/site-packages (0.37.1)
Installing collected packages: setuptools, pip
Successfully installed pip-22.2.2 setuptools-65.3.0

[notice] A new release of pip available: 22.2.1 -> 22.2.2
[notice] To update, run: pip install --upgrade pip
```

Install the package

```console
$ python -m pip install ./torch-1.12.1-cp39-cp39-manylinux1_x86_64.whl
```

Now it should appear to pip as installed.

```console
$ pip install torch==1.12.1
Defaulting to user installation because normal site-packages is not writeable
Requirement already satisfied: torch==1.12.1 in ./.local/lib/python3.9/site-packages (1.12.1)
Requirement already satisfied: typing-extensions in ./.local/lib/python3.9/site-packages (from torch==1.12.1) (4.3.0)
```