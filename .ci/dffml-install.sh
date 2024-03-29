#!/usr/bin/env bash
set -xe

if [ "x${DFFML_RELEASE}" == "xmain" ]; then
  pip install -e .[dev]
  dffml service dev install
elif [ "x${DFFML_RELEASE}" == "xlatest" ]; then
  pip install dffml[all]
else
  pip install "dffml[all]==${DFFML_RELEASE}"
fi
