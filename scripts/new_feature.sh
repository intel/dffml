#!/usr/bin/env bash
set -xe

NAME="$1"

if [ "x$NAME" = "x" ]; then
  echo "Usage: $0 new_feature_name" >&2
  exit 1
fi

MODULE_PATH="$(dirname "$0")/.."
realpath $MODULE_PATH

rm -rf "${MODULE_PATH}/feature/${NAME}"
cp -r "${MODULE_PATH}/scripts/skel/feature/" "${MODULE_PATH}/feature/${NAME}"

cd "${MODULE_PATH}/feature/${NAME}"
mv dffml_feature_feature_name/ "dffml_feature_${NAME}/"
find . -type f -exec sed -i "s/FEATURE_NAME/${NAME}/g" {} \;
find . -type f -exec sed -i "s/feature_name/${NAME}/g" {} \;
python3.7 -m pip install -e .
python3.7 setup.py test
