#!/usr/bin/env sh
set -e

PYTHON=${PYTHON:-"python3.7"}

rm -rf pages
# changelog.md
if [ ! -f docs/changelog.md ]; then
  ln -s "${PWD}/CHANGELOG.md" docs/changelog.md
fi
# shouldi.md
if [ ! -f docs/shouldi.md ]; then
  ln -s "${PWD}/examples/shouldi/README.md" docs/shouldi.md
fi
# docs/contributing/consoletest.md
if [ ! -f docs/contributing/consoletest.md ]; then
  ln -s "${PWD}/dffml/util/testing/consoletest/README.md" docs/contributing/consoletest.md
fi
# HTTP Service
mkdir -p docs/plugins/service/
rm -f docs/plugins/service/http
ln -s "${PWD}/service/http/docs/" docs/plugins/service/http
# Main docs
"${PYTHON}" scripts/docs.py
"${PYTHON}" scripts/docs_api.py
"${PYTHON}" -c 'import os, pkg_resources; [e.load() for e in pkg_resources.iter_entry_points("console_scripts") if e.name.startswith("sphinx-build")][0]()' -W -b html docs pages \
  || (echo "[ERROR] Failed run sphinx, is it installed (pip install -U .[dev])?" 1>&2 ; exit 1)
cp -r docs/images pages/
if [ ! -f pages/_static/copybutton.js ]; then
  curl -sSL -o pages/_static/copybutton.js "https://raw.githubusercontent.com/python/python-docs-theme/master/python_docs_theme/static/copybutton.js"
fi
sha384sum -c - <<EOF
bf80c778867bd87d14588ff72ae10632b331427379a299ab2ac4d7ddefa9b648313720b796ab441359e0e47daf738109 pages/_static/copybutton.js
EOF
touch pages/.nojekyll

if [ "x${HTTP}" != "x" ]; then
  "${PYTHON}" -m http.server --directory pages/ 8080
fi
