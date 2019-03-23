#!/usr/bin/env bash
set -ex

function run_plugin() {
  python setup.py install && cd $PLUGIN && coverage run setup.py test && cd -

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
  added_to_changelog=$(git diff origin/master --numstat - CHANGELOG.md \
    | awk '{print $1}')
  if [ $added_to_changelog -eq 0 ]; then
    echo "No changes to CHANGELOG.md" >&2
    exit 1
  fi
}

if [ "x$PLUGIN" != "x" ]; then
  run_plugin
else if [ "x$CHANGELOG" != "x" ]; then
  run_changelog
fi
