#!/usr/bin/env bash
set -e

if [ -d "$HOME/.local/bin" ]; then
  export PATH="$HOME/.local/bin:$PATH"
fi

SRC_ROOT=${SRC_ROOT:-"${PWD}"}
PYTHON=${PYTHON:-"python3.7"}

TEMP_DIRS=()

function run_plugin() {
  # Create a virtualenv
  venv_dir="$(mktemp -d)"
  TEMP_DIRS+=("${venv_dir}")
  "${PYTHON}" -m venv "${venv_dir}"
  source "${venv_dir}/bin/activate"
  "${PYTHON}" -m pip install -U pip

  "${PYTHON}" -m pip install -U "${SRC_ROOT}"

  cd "${PLUGIN}"
  "${PYTHON}" setup.py test
  cd -

  if [ "x${PLUGIN}" = "x." ]; then
    # Try running create command
    plugin_creation_dir="$(mktemp -d)"
    TEMP_DIRS+=("${plugin_creation_dir}")
    cd "${plugin_creation_dir}"
    # Plugins we know how to make
    PLUGINS=(\
      "model" \
      "operations" \
      "service" \
      "source" \
      "config")
    for plugin in ${PLUGINS[@]}; do
      dffml service dev create "${plugin}" "ci-test-${plugin}"
      cd "ci-test-${plugin}"
      "${PYTHON}" -m pip install -U .
      "${PYTHON}" setup.py test
      cd "${plugin_creation_dir}"
    done

    # Run the examples
    cd "${SRC_ROOT}/examples"
    "${PYTHON}" -m pip install -r requirements.txt
    "${PYTHON}" -m unittest discover

    # Deactivate venv
    deactivate

    # Create the docs
    cd "${SRC_ROOT}"
    "${PYTHON}" -m pip install -U -e "${SRC_ROOT}[dev]"
    "${PYTHON}" -m dffml service dev install
    ./scripts/docs.sh

    # Run with coverage
    "${PYTHON}" -m coverage run setup.py test
  fi
}

function run_changelog() {
  # Only run this check on pull requests
  if [ "x$GITHUB_EVENT_NAME" != "xpull_request" ]; then
    exit 0
  fi
  # Ensure the number of lines added in the changelog is not 0
  added_to_changelog=$(git diff origin/master --numstat -- CHANGELOG.md \
    | awk '{print $1}')
  if [ "x$added_to_changelog" == "x" ] || [ "$added_to_changelog" -eq 0 ]; then
    echo "No changes to CHANGELOG.md" >&2
    exit 1
  fi
}

function run_whitespace() {
  export whitespace=$(mktemp -u)
  function rmtempfile () {
    rm -f "$whitespace"
  }
  trap rmtempfile EXIT
  ( find dffml -type f -name \*.py -exec grep -EHn " +$" {} \; ) 2>&1 \
    | tee "$whitespace"
  lines=$(wc -l < "$whitespace")
  if [ "$lines" -ne 0 ]; then
    echo "Trailing whitespace found" >&2
    exit 1
  fi
}

function run_style() {
  black --check "${SRC_ROOT}"
}

function cleanup_temp_dirs() {
  if [ "x${NO_RM_TEMP}" != "x" ]; then
    return
  fi
  for temp_dir in ${TEMP_DIRS[@]}; do
    rm -rf "${temp_dir}"
  done
}

# Clean up temporary directories on exit
trap cleanup_temp_dirs EXIT

if [ "x${PLUGIN}" != "x" ]; then
  run_plugin
elif [ "x${CHANGELOG}" != "x" ]; then
  run_changelog
elif [ "x${WHITESPACE}" != "x" ]; then
  run_whitespace
elif [ "x${STYLE}" != "x" ]; then
  run_style
fi
