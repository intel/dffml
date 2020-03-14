#!/usr/bin/env bash
set -xe

SRC_ROOT=${SRC_ROOT:-"${PWD}"}
PYTHON=${PYTHON:-"python3.7"}

PLUGINS=("${SRC_ROOT}/" \
	"${SRC_ROOT}/configloader/yaml" \
	"${SRC_ROOT}/model/tensorflow" \
	"${SRC_ROOT}/model/scratch" \
	"${SRC_ROOT}/model/scikit" \
	"${SRC_ROOT}/examples/shouldi" \
	"${SRC_ROOT}/feature/git" \
	"${SRC_ROOT}/feature/auth" \
	"${SRC_ROOT}/service/http" \
	"${SRC_ROOT}/source/mysql")
for PLUGIN in ${PLUGINS[@]}; do
  cd "${PLUGIN}"
  git clean -xdf
  "${SRC_ROOT}/scripts/upload.sh"
  # Go back to main source directory
  cd "${SRC_ROOT}"
done
