FROM docker.io/library/python:3.9@sha256:30678bb79d9eeaf98ec0ce83cdcd4d6f5301484ef86873a711e69df2ca77e8ac AS builder

COPY images_containers_manifest.py /images_containers_manifest.py

ENTRYPOINT /images_containers_manifest.py
