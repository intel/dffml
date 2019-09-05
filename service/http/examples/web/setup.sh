#!/usr/bin/env bash

export PORT=${PORT:-"8080"}

curl -X POST -H "Content-Type: application/json" -d @config.json \
  http://127.0.0.1:${PORT}/configure/source/json/mydataset
