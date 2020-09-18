#!/usr/bin/env bash
set -xe

rm -rf consoletest
exec python3 -u -c 'import os, pkg_resources; [e.load() for e in pkg_resources.iter_entry_points("console_scripts") if e.name.startswith("sphinx-build")][0]()' -b consoletest docs consoletest
