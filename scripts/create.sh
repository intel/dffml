#!/usr/bin/env bash
set -e

PROJECT_TYPE="$1"
NAME="$2"

MODULE_PATH="$(dirname "$0")/.."
SKEL="${MODULE_PATH}/scripts/skel/${PROJECT_TYPE}/"

if [ "x$PROJECT_TYPE" = "x" ] || [ "x$NAME" = "x" ]; then
  echo "Usage: $0 feature|model name_of_new_thing" >&2
  exit 1
fi

if [ ! -d "${SKEL}" ]; then
  echo "${PROJECT_TYPE} not found in $(ls "${MODULE_PATH}/scripts/skel/")" >&2
  exit 1
fi

rm -rf "${MODULE_PATH}/${PROJECT_TYPE}/${NAME}"
cp -r "${SKEL}" "${MODULE_PATH}/${PROJECT_TYPE}/${NAME}"

cd "${MODULE_PATH}/${PROJECT_TYPE}/${NAME}"
mv "dffml_${PROJECT_TYPE}_${PROJECT_TYPE}_name/" "dffml_${PROJECT_TYPE}_${NAME}/"
find . -type f -exec sed -i "s/${PROJECT_TYPE}_name/${NAME}/g" {} \;
python3.7 -m pip install -e .
python3.7 setup.py test
