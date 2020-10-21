#!/usr/bin/env bash
set -xe

. "${CONDA_INSTALL_LOCATION}/miniconda${PYTHON_SHORT_VERSION}/bin/activate" base

if [ "x${DFFML_RELEASE}" == "xmaster" ]; then
  pip install -e .
  dffml service dev install
elif [ "x${DFFML_RELEASE}" == "xlatest" ]; then
  pip install --use-feature=2020-resolver dffml[all]
else
  pip install --use-feature=2020-resolver "dffml[all]==${DFFML_RELEASE}"
fi
