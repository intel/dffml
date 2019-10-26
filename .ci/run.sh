#!/usr/bin/env bash
set -e

if [ -d "$HOME/.local/bin" ]; then
  export PATH="$HOME/.local/bin:$PATH"
fi

function run_plugin() {
  python setup.py install
  cd "$PLUGIN"
  coverage run setup.py test
  coverage report -m
  cd -

  if [ "x$PLUGIN" = "x." ]; then
    cd examples
    python -m pip install -r requirements.txt
    python -m unittest discover
    cd ..
    ./scripts/docs.sh
    # Try running create for real
    cd $(mktemp -d)
    # TODO Bash array
    # Create model
    dffml service dev create model travis-test-model
    cd travis-test-model
    python setup.py install
    python setup.py test
    cd ..
    # Create operations
    dffml service dev create operations travis-test-operations
    cd travis-test-operations
    python setup.py install
    python setup.py test
    cd ..
    # Create service
    dffml service dev create service travis-test-service
    cd travis-test-service
    python setup.py install
    python setup.py test
    cd ..
    # Create source
    dffml service dev create source travis-test-source
    cd travis-test-source
    python setup.py install
    python setup.py test
    cd ..
    # Create config
    dffml service dev create config travis-test-config
    cd travis-test-config
    python setup.py install
    python setup.py test
    cd ..
  fi
}

function run_changelog() {
  # Only run this check on pull requests
  if [ "x$TRAVIS_PULL_REQUEST" == "xfalse" ]; then
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
  black --check .
}

if [ "x$PLUGIN" != "x" ]; then
  run_plugin
elif [ "x$CHANGELOG" != "x" ]; then
  run_changelog
elif [ "x$WHITESPACE" != "x" ]; then
  run_whitespace
elif [ "x$STYLE" != "x" ]; then
  run_style
fi
