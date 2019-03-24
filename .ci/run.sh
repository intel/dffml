#!/usr/bin/env bash
set -e

function run_plugin() {
  python setup.py install && cd "$PLUGIN" && coverage run setup.py test && cd -

  if [ "x$PLUGIN" = "x." ]; then
    ./scripts/create.sh feature travis_test_feature
    ./scripts/create.sh model travis_test_model
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

if [ "x$PLUGIN" != "x" ]; then
  run_plugin
elif [ "x$CHANGELOG" != "x" ]; then
  run_changelog
elif [ "x$WHITESPACE" != "x" ]; then
  run_whitespace
fi
