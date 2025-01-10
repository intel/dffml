FROM docker.io/library/python:3.12@sha256:2eedc86b81f2336841f4eed06dff14937d37ec172eec655434fd478eacb1ea49 AS builder

COPY images_containers_manifest.py /images_containers_manifest.py

ENTRYPOINT /images_containers_manifest.py
