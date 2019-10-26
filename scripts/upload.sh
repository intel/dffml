#!/usr/bin/env bash

rm -rf dist && git clean -fdx && python3.7 setup.py sdist && twine upload dist/*
