# Installation

## pyenv

If you don't have Python 3.7 and it's not installable by your package manager,
`pyenv` is a very easy way to install another version of Python.

https://github.com/pyenv/pyenv-installer

## Docker

This is a good option if you don't want to deal with installing Python 3.7 or
don't like `pyenv`.

```console
docker pull intelotc/dffml
```

Or build it yourself.

```console
docker build -t dffml .
```

You can then make bash function to run the dffml docker container.

```bash
dffml() {
  docker run --rm -ti \
    -v $HOME/.local:/home/$USER/.local/ \
    -v $HOME/.cache:/home/$USER/.cache/ \
    -v $PWD:/workdir -w /workdir -e UID=$(id -u) -e USER=$USER dffml $@
}
```

This creates an alias that takes your current working directory and mounts it
into `/workdir` as well as your `$HOME/.local` to the same in the container.

With the alias, you can run `dffml` commands as you would if installed via
`pip`.

```console
dffml list
```

Keep in mind that if you're working on files they can only be ones in your
current working directory, and if you want to access network resources and they
are on your host, you'll have to talk to `172.17.0.1` (docker0 inet address)
instead of `localhost` or `127.0.0.1`.

The purpose of mounting `$HOME/.local` is so that if you want to
`pip install` anything, you can, and it will persist between invocations due
to that being on the host.

If you wan to run `pip` you can put it after `dffml`.

```console
dffml pip install example
```
