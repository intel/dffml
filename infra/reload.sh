#!/usr/bin/env bash
exec docker exec caddy kill -s USR1 1
