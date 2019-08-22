#!/usr/bin/env sh
set -e

rm -rf pages
python3.7 scripts/docs.py
python3.7 -c 'import os, pkg_resources; [e.load() for e in pkg_resources.iter_entry_points("console_scripts") if e.name.startswith("sphinx-build")][0]()' -b html docs pages
find pages/ -name \*.html -exec \
  sed -i 's/<span class="gp">\&gt;\&gt;\&gt; <\/span>//g' {} \;
cp -r docs/images pages/
touch pages/.nojekyll
