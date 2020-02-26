#!/usr/bin/env sh
set -e

rm -rf doctest
python3.7 -c 'import os, pkg_resources; [e.load() for e in pkg_resources.iter_entry_points("console_scripts") if e.name.startswith("sphinx-build")][0]()' -b doctest docs doctest
