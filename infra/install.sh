#!/usr/bin/env bash
set -xe

cp -v systemd/* /etc/systemd/system/
systemctl enable --now $(cd systemd && echo *.service)
