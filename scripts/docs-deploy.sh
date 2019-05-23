#!/usr/bin/env sh
set -e

rm -rf pages/.git
cp -r .git pages/.git
cd pages/
git branch -D gh-pages
git checkout --orphan gh-pages
git add -A
git commit -sam 'gh-pages'
git push -u origin -f gh-pages
