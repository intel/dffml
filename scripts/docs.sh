#!/usr/bin/env sh
set -e

PYTHON=${PYTHON:-"python3.7"}

rm -rf pages
# HTTP Service
mkdir -p docs/plugins/service/
rm -f docs/plugins/service/http
ln -s "${PWD}/service/http/docs/" docs/plugins/service/http
# Main docs
"${PYTHON}" scripts/docs.py
"${PYTHON}" scripts/docs_api.py
"${PYTHON}" -c 'import os, pkg_resources; [e.load() for e in pkg_resources.iter_entry_points("console_scripts") if e.name.startswith("sphinx-build")][0]()' -b html docs pages \
  || (echo "[ERROR] Failed run sphinx, is it installed (pip install -U .[dev])?" 1>&2 ; exit 1)
cp -r docs/images pages/
curl -sSL -o pages/_static/copybutton.js "https://raw.githubusercontent.com/python/python-docs-theme/master/python_docs_theme/static/copybutton.js"
sha384sum -c - <<EOF
bf80c778867bd87d14588ff72ae10632b331427379a299ab2ac4d7ddefa9b648313720b796ab441359e0e47daf738109 pages/_static/copybutton.js
EOF
touch pages/.nojekyll

if [ "x${HTTP}" != "x" ]; then
  "${PYTHON}" -m http.server --directory pages/ 8080
fi
