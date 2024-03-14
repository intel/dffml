```console
$ docker run --rm -ti -e AGENT_TOOLSDIRECTORY=/tmp/tools -e "INPUT_PYTHON_VERSION=3.11" -e 'INPUT_CHECK_LATEST=false' -e 'INPUT_ALLOW_PRERELEASES=false' -e 'INPUT_UPDATE_ENVIRONMENT=false' -e 'RUNNER_TEMP=/tmp/' -v $PWD:/src/setup-python -w /src/setup-python node dist/setup/index.js
```