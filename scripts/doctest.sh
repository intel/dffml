#!/usr/bin/env bash

if [ "x${1}" == "x" ]; then
  echo "Usage: ${0} class_or_func_name_in_dffml" 1>&2
  exit 1
fi

exec python -c "import doctest, dffml; print(doctest.script_from_examples(dffml.${1}.__doc__))"
