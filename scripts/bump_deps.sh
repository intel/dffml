#!/usr/bin/env bash
# Update all dependents of DFFML so that they require the latest version

VERSION="$(dffml service dev setuppy kwarg version setup.py)"

for file in $(git grep "dffml>=.*\\." | sed 's/:.*//g'); do
  sed -i "s/dffml>=.*\"/dffml>=${VERSION}\"/g" "${file}";
done
