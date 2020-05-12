#!/usr/bin/env bash
set -xe

if [ "x${NO_STRICT}" != "x" ]; then
  set +e
fi

SRC_ROOT=${SRC_ROOT:-"${PWD}"}
PYTHON=${PYTHON:-"python3.7"}

PLUGINS=("${SRC_ROOT}/" \
	"${SRC_ROOT}/configloader/yaml" \
	"${SRC_ROOT}/model/tensorflow" \
	"${SRC_ROOT}/model/scratch" \
	"${SRC_ROOT}/model/scikit" \
	"${SRC_ROOT}/examples/shouldi" \
	"${SRC_ROOT}/operations/deploy" \
	"${SRC_ROOT}/feature/git" \
	"${SRC_ROOT}/feature/auth" \
	"${SRC_ROOT}/service/http" \
	"${SRC_ROOT}/source/mysql")
for PLUGIN in ${PLUGINS[@]}; do
  cd "${PLUGIN}"
  "${PYTHON}" setup.py test
  exit_code=$?
  if [ "x${exit_code}" == "x0" ]; then
    echo "[PASS]: ${PLUGIN}"
  else
    echo "[FAIL]: ${PLUGIN}"
  fi
  # Test example and skel if main
  if [ "x${PLUGIN}" == "x${SRC_ROOT}/" ]; then
    # Test examples
    cd examples
    "${PYTHON}" -m pip install -r requirements.txt
    "${PYTHON}" -m unittest discover
    cd -
    # Generate docs
    "${SRC_ROOT}/scripts/docs.sh"
    # Create venv
    TMP_DIR="$(mktemp -d)"
    # Remove temporary directory when done
    trap "rm --preserve-root=all -rf ${TMP_DIR}" EXIT
    "${PYTHON}" -m venv "${TMP_DIR}/.venv"
    cd "${TMP_DIR}"
    # Activate venv
    source "${TMP_DIR}/.venv/bin/activate"
    # Ensure that the python we're using is from the venv
    which "${PYTHON}" | grep -q "${TMP_DIR}"
    # Install DFFML to venv
    "${PYTHON}" -m pip install "${SRC_ROOT}/"
    # Create plugins
    SKELS=("model" \
      "operations" \
      "service" \
      "source" \
      "config")
    for SKEL in ${SKELS[@]}; do
      dffml service dev create "${SKEL}" "test-${SKEL}"
      cd "test-${SKEL}"
      "${PYTHON}" setup.py install
      "${PYTHON}" setup.py test
      cd -
    done
    # Deactivate venv
    deactivate
  fi
  # Go back to main source directory
  cd "${SRC_ROOT}"
done
