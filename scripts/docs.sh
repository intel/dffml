#!/usr/bin/env sh
set -e

rm -rf pages
python3.7 scripts/docs.py
sphinx-build -b html docs pages
find pages/ -name \*.html -exec \
  sed -i 's/<span class="gp">\&gt;\&gt;\&gt; <\/span>//g' {} \;
cp -r docs/images pages/
touch pages/.nojekyll
