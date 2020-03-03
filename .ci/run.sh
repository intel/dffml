#!/usr/bin/env bash
set -ex

if [ -d "$HOME/.local/bin" ]; then
  export PATH="$HOME/.local/bin:$PATH"
fi

SRC_ROOT=${SRC_ROOT:-"${PWD}"}
PYTHON=${PYTHON:-"python3.7"}

TEMP_DIRS=()

function run_plugin_examples() {
  cd "${SRC_ROOT}/${PLUGIN}/examples"
  if [ -f "requirements.txt" ]; then
    "${PYTHON}" -m pip install -r requirements.txt
  fi
  # Run example tests in top level examples directory
  for dir in $(find . -type d); do
    # Skip shouldi if we're in the root package
    set +e
    within_shouldi=$(echo "${dir}" | grep "shouldi")
    set -e
    if [ "x${PLUGIN}" != "x." ] && [ "x${within_shouldi}" != "x" ]; then
      continue
    fi
    # Run example tests in examples subdirectories
    cd "${SRC_ROOT}/${PLUGIN}/examples"
    cd "${dir}"
    "${PYTHON}" -m unittest discover -v
  done
  cd "${SRC_ROOT}/${PLUGIN}"
}

function run_plugin() {
  # Create a virtualenv
  venv_dir="$(mktemp -d)"
  TEMP_DIRS+=("${venv_dir}")
  "${PYTHON}" -m venv "${venv_dir}"
  source "${venv_dir}/bin/activate"
  "${PYTHON}" -m pip install -U pip twine

  "${PYTHON}" -m pip install -U -e "${SRC_ROOT}"

  if [ "x${PLUGIN}" = "xmodel/tensorflow_hub" ]; then
    "${PYTHON}" -m pip install -U -e "${SRC_ROOT}/model/tensorflow"
  fi

  cd "${PLUGIN}"
  PACKAGE_NAME=$(dffml service dev setuppy kwarg name setup.py)
  # Install
  "${PYTHON}" -m pip install -e .
  # Run the tests
  "${PYTHON}" setup.py test
  # Run examples if they exist and we aren't at the root
  if [ -d "examples" ] && [ "x${PLUGIN}" != "x." ]; then
    run_plugin_examples
  fi
  cd "${SRC_ROOT}"

  if [ "x${PLUGIN}" = "x." ]; then
    exit 0
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

    # Install all the plugins so examples can use them
    "${PYTHON}" -m pip install -U -e "${SRC_ROOT}"
    "${PYTHON}" -m dffml service dev install

    # Run the examples
    run_plugin_examples

    # Deactivate venv
    deactivate

    # Create the docs
    "${PYTHON}" -m pip install -U -e "${SRC_ROOT}[dev]"
    "${PYTHON}" -m dffml service dev install -user
    "${SRC_ROOT}/scripts/docs.sh"

    # Log skipped tests to file
    check_skips="$(mktemp)"
    TEMP_DIRS+=("${check_skips}")

    # Run with coverage
    "${PYTHON}" -m coverage run setup.py test 2>&1 | tee "${check_skips}"
    "${PYTHON}" -m coverage report -m

    # Fail if any tests were skipped or errored
    skipped=$(grep -E '(skipped=.*)' "${check_skips}" | wc -l)
    if [ "$skipped" -ne 0 ]; then
      echo "Tests were skipped" >&2
      exit 1
    fi

    errors=$(grep -E '(errors=.*)' "${check_skips}" | wc -l)
    if [ "$errors" -ne 0 ]; then
      echo "Tests errored" >&2
      exit 1
    fi
  fi

  if [ "x${GITHUB_ACTIONS}" == "xtrue" ] && [ "x${GITHUB_REF}" == "xrefs/heads/master" ]; then
    git status
    dffml service dev release "${PLUGIN}"
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
  find . -type f -name '*.py' -exec grep -EHn " +$" {} \; 2>&1 > "$whitespace"
  lines=$(wc -l < "$whitespace")
  if [ "$lines" -ne 0 ]; then
    echo "Trailing whitespace found" >&2
    cat "${whitespace}" >&2
    exit 1
  fi
}

function run_style() {
  black --check "${SRC_ROOT}"

  for filename in $(git ls-files \*.js); do
    echo "Checking JavaScript file \'${filename}\'"
    diff <(js-beautify -n -s 2 "${filename}") "${filename}"
  done
}

function run_docs() {
  export GIT_SSH_COMMAND='ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no'

  cd "${SRC_ROOT}"
  "${PYTHON}" -m pip install --prefix=~/.local -U -e "${SRC_ROOT}[dev]"
  "${PYTHON}" -m dffml service dev install -user

  last_release=$("${PYTHON}" -m dffml service dev setuppy kwarg version setup.py)

  # Doctests
  ./scripts/doctest.sh

  # Make master docs
  master_docs="$(mktemp -d)"
  TEMP_DIRS+=("${master_docs}")
  rm -rf pages
  ./scripts/docs.sh
  mv pages "${master_docs}/html"

  # Make last release docs
  release_docs="$(mktemp -d)"
  TEMP_DIRS+=("${release_docs}")
  rm -rf pages
  git clean -fdx
  git reset --hard HEAD
  echo "Checking out last release ${last_release}"
  git checkout "${last_release}"
  git clean -fdx
  git reset --hard HEAD
  # Uninstall dffml
  "${PYTHON}" -m pip uninstall -y dffml
  # Remove .local to force install of correct dependency versions
  rm -rf ~/.local
  "${PYTHON}" -m pip install --prefix=~/.local -U -e "${SRC_ROOT}[dev]"
  "${PYTHON}" -m dffml service dev install -user
  ./scripts/docs.sh
  mv pages "${release_docs}/html"

  git clone https://github.com/intel/dffml -b gh-pages \
    "${release_docs}/old-gh-pages-branch"

  mv "${release_docs}/old-gh-pages-branch/.git" "${release_docs}/html/"
  mv "${master_docs}/html" "${release_docs}/html/master"

  # Make webui
  git clone https://github.com/intel/dffml -b webui "${release_docs}/webui"
  cd "${release_docs}/webui/service/webui/webui"
  yarn install
  yarn build
  mv build/ "${release_docs}/html/master/webui"

  cd "${release_docs}/html"

  git config user.name 'John Andersen'
  git config user.email 'johnandersenpdx@gmail.com'

  git add -A
  git commit -sam "docs: $(date)"

  # Don't push docs unless we're running on master
  if [ "x${GITHUB_ACTIONS}" == "xtrue" ] && [ "x${GITHUB_REF}" != "xrefs/heads/master" ]; then
    return
  fi

  mkdir -p ~/.ssh
  chmod 700 ~/.ssh
  "${PYTHON}" -c "import pathlib, base64, os; keyfile = pathlib.Path('~/.ssh/github_dffml').expanduser(); keyfile.write_bytes(b''); keyfile.chmod(0o600); keyfile.write_bytes(base64.b32decode(os.environ['GITHUB_PAGES_KEY']))"
  ssh-keygen -y -f ~/.ssh/github_dffml > ~/.ssh/github_dffml.pub
  export GIT_SSH_COMMAND="${GIT_SSH_COMMAND} -o IdentityFile=~/.ssh/github_dffml"

  git remote set-url origin git@github.com:intel/dffml
  git push -f

  cd -

  git reset --hard HEAD
  git checkout master
}

function run_lines() {
  "${PYTHON}" ./scripts/check_literalincludes.py
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
elif [ "x${DOCS}" != "x" ]; then
  run_docs
elif [ "x${LINES}" != "x" ]; then
  run_lines
fi
