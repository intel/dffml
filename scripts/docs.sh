#!/usr/bin/env sh
set -e

rm -rf pages
# HTTP Service
mkdir -p docs/plugins/service/
rm -f docs/plugins/service/http
ln -s "${PWD}/service/http/docs/" docs/plugins/service/http
# Main docs
python3.7 scripts/docs.py
python3.7 -c 'import os, pkg_resources; [e.load() for e in pkg_resources.iter_entry_points("console_scripts") if e.name.startswith("sphinx-build")][0]()' -b html docs pages \
  || (echo "[ERROR] Failed run sphinx, is it installed (pip install -U .[dev])?" 1>&2 ; exit 1)
cp -r docs/images pages/
wget -P pages/_static "https://raw.githubusercontent.com/python/python-docs-theme/master/python_docs_theme/static/copybutton.js"
touch pages/.nojekyll
