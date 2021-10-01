#!/usr/bin/env bash
set -ex

if [ -d "$HOME/.local/bin" ]; then
  export PATH="$HOME/.local/bin:$PATH"
fi

SRC_ROOT=${SRC_ROOT:-"${PWD}"}
PYTHON=${PYTHON:-"python3"}
if [ "x${VIRTUAL_ENV}" != "x" ]; then
  PYTHON="python"
fi

TEMP_DIRS=()

# Copy temporary fixes to a temporary directory in case we change branches
TEMPFIX="$(mktemp -d)"
TEMP_DIRS+=("${TEMPFIX}")
cp -r ${SRC_ROOT}/scripts/tempfix/* "${TEMPFIX}/"

python_version="$(${PYTHON} -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"

function run_plugin_examples() {
  if [ ! -d "${SRC_ROOT}/${PLUGIN}/examples" ]; then
    return
  fi
  cd "${SRC_ROOT}/${PLUGIN}/examples"
  if [ -f "requirements.txt" ]; then
    "${PYTHON}" -m pip install -r requirements.txt
  fi
  "${PYTHON}" -m unittest discover -v
  cd "${SRC_ROOT}/${PLUGIN}"
}

test_no_skips() {
  # Log skipped tests to file
  check_skips="$(mktemp)"
  TEMP_DIRS+=("${check_skips}")

  # Run all if nothing given
  if [ "x$@" == "x" ]; then
    UNITTEST_ARGS="discover -v"
  else
    UNITTEST_ARGS=$@
  fi

  # Run with coverage
  TEST_DOCS=1 "${PYTHON}" -u -m coverage run -m unittest $UNITTEST_ARGS 2>&1 | tee "${check_skips}"
  "${PYTHON}" -m coverage report -m

  # Fail if any coroutines were not awaited
  unawaited=$(grep -nE 'coroutine .* was never awaited' "${check_skips}" | wc -l)
  if [ "$unawaited" -ne 0 ]; then
    echo "Found un-awaited coroutines" >&2
    exit 1
  fi

  # Fail if any tests were skipped or errored
  skipped=$(tail -n 1 "${check_skips}" | grep -E '(skipped=[0-9]+)' | wc -l)
  if [ "$skipped" -ne 0 ]; then
    echo "Tests were skipped" >&2
    exit 1
  fi

  errors=$(grep -E '(errors=[0-9]+)' "${check_skips}" | wc -l)
  if [ "$errors" -ne 0 ]; then
    echo "Tests errored" >&2
    exit 1
  fi

  failures=$(grep -E '(failures=[0-9]+)' "${check_skips}" | wc -l)
  if [ "$failures" -ne 0 ]; then
    echo "Tests failed" >&2
    exit 1
  fi
}

function run_plugin() {
  export PLUGIN="${1}"

  cd "${SRC_ROOT}/${PLUGIN}"

  # Install plugin
  "${PYTHON}" -m pip install -U -e .[dev]

  if [ "x${PLUGIN}" != "x." ]; then
    # Test ensuring no tests were skipped
    test_no_skips
    # Run examples if they exist and we aren't at the root
    run_plugin_examples
  else
    # If we are at the root. Install plugsin and run various integration tests

    # Run the tests but not the long documentation consoletests
    "${PYTHON}" -u -m unittest discover -v

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
      "${PYTHON}" -m unittest discover -v
      cd "${plugin_creation_dir}"
    done

    # Install all the plugins so examples can use them
    "${PYTHON}" -m dffml service dev install

    # Run the examples
    run_plugin_examples

    # Test ensuring no tests were skipped
    test_no_skips
  fi

  cd "${SRC_ROOT}"

  # Report installed versions of packages
  "${PYTHON}" -m pip freeze

  if [[ "x${GITHUB_ACTIONS}" == "xtrue" ]] && \
     [[ "x${GITHUB_REF}" =~ xrefs/heads/[a-zA-Z0-9]*\.[a-zA-Z0-9]*\.[a-zA-Z0-9]* ]]; then
    git status
    dffml service dev release "${PLUGIN}"
  fi
}

function run_consoletest() {
  export PLUGIN="${1/docs\//}"
  export PLUGIN="${PLUGIN//\//_}"
  export PLUGIN="${PLUGIN/\.rst/}"

  cd "${SRC_ROOT}"

  # Log tests to file
  test_log="$(mktemp)"
  TEMP_DIRS+=("${test_log}")

  # Install base package with testing and development utilities
  "${PYTHON}" -m pip install -U -e ".[dev]"

  test_no_skips -v "tests.docs.test_consoletest.TestDocs.test_${PLUGIN}"

  cd "${SRC_ROOT}"

  git status
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
  find . -type f -name '*.py' -o -name '*.rst' -o -name '*.md' -exec grep -EHn " +$" {} \; 2>&1 > "$whitespace"
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

function run_commit(){
  BRANCH="$(echo $GITHUB_REF | cut -d'/' -f 3)"
  echo "On Branch: ${BRANCH}"
  if [[ "$BRANCH" != "master" ]]; then
    dffml service dev lint commits
  fi
}

function run_imports(){
  dffml service dev lint imports
  if [[ -z $(git status -s) ]]
  then
    echo "Yay ! No unused imports found"
  else
    echo "There maybe unused imports in the following files:"
    git status -s  | grep "M" | awk '{print $2}'
    exit 1
  fi

}

function run_docs() {
  export GIT_SSH_COMMAND='ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no'

  cd "${SRC_ROOT}"
  "${PYTHON}" -m pip install --prefix=~/.local -U -e "${SRC_ROOT}[dev]"
  "${PYTHON}" -m dffml service dev install -user

  last_release=$(git log -p -- dffml/version.py \
                 | grep \+VERSION \
                 | grep -v rc \
                 | sed -e 's/.* = "//g' -e 's/"//g' \
                 | head -n 1)

  # Fail if there are any changes to the Git repo
  changes=$(git status --porcelain | wc -l)
  if [ "$changes" -ne 0 ]; then
    echo "Running docs.py resulted in changes to the Git repo" >&2
    echo "Need to run dffml service dev docs and commit changes" >&2
    exit 1
  fi

  # Make master docs
  master_docs="$(mktemp -d)"
  TEMP_DIRS+=("${master_docs}")
  rm -rf pages
  dffml service dev docs || ./scripts/docs.sh

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
  dffml service dev docs || ./scripts/docs.sh
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

  ssh_key_dir="$(mktemp -d)"
  TEMP_DIRS+=("${ssh_key_dir}")
  mkdir -p ~/.ssh
  chmod 700 ~/.ssh
  "${PYTHON}" -c "import pathlib, base64, os; keyfile = pathlib.Path(\"${ssh_key_dir}/github\").absolute(); keyfile.write_bytes(b''); keyfile.chmod(0o600); keyfile.write_bytes(base64.b32decode(os.environ['SSH_DFFML_GH_PAGES']))"
  ssh-keygen -y -f "${ssh_key_dir}/github" > "${ssh_key_dir}/github.pub"
  export GIT_SSH_COMMAND="${GIT_SSH_COMMAND} -o IdentityFile=${ssh_key_dir}/github"

  git remote set-url origin git@github.com:intel/dffml
  git push -f

  cd -

  git reset --hard HEAD
  git checkout master
}

function run_lines() {
  "${PYTHON}" ./scripts/check_literalincludes.py
}

function run_container() {
  docker build --build-arg DFFML_RELEASE=master -t intelotc/dffml .
  docker run --rm intelotc/dffml version
  docker run --rm intelotc/dffml service dev entrypoints list dffml.model
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

if [ "x${1}" == "xchangelog" ]; then
  run_changelog
elif [ "x${1}" == "xwhitespace" ]; then
  run_whitespace
elif [ "x${1}" == "xstyle" ]; then
  run_style
elif [ "x${1}" == "xcommit" ]; then
  run_commit
elif [ "x${1}" == "ximport" ]; then
  run_imports
elif [ "x${1}" == "xdocs" ]; then
  run_docs
elif [ "x${1}" == "xlines" ]; then
  run_lines
elif [ "x${1}" == "xcontainer" ]; then
  run_container
elif [ "x${1}" == "xconsoletest" ]; then
  run_consoletest "${2}"
elif [ -d "${1}" ]; then
  run_plugin "${1}"
else
  echo "Not sure what to do" 2>&1
  exit 1
fi
