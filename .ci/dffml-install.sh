#!/usr/bin/env bash
set -xe

if [ "x${DFFML_RELEASE}" == "xmaster" ]; then
  pip install -e .
  dffml service dev install
elif [ "x${DFFML_RELEASE}" == "xlatest" ]; then
  pip install dffml[all]
else
  pip install "dffml[all]==${DFFML_RELEASE}"
fi
python scripts/tempfix/pytorch/pytorch/46930.py
