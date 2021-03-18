#!/usr/bin/env bash

if [ "x${1}" == "x" ]; then
  echo "Usage: ${0} class_or_func_name_in_dffml" 1>&2
  exit 1
fi

export OBJ="${1}"
exec python -m black --config pyproject.toml -c "$(python -c 'import os, doctest, dffml; print(doctest.script_from_examples(getattr(dffml, os.environ["OBJ"]).__doc__))')"
