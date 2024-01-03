FROM docker.io/library/python:3.12@sha256:3733015cdd1bd7d9a0b9fe21a925b608de82131aa4f3d397e465a1fcb545d36f AS builder

COPY images_containers_manifest.py /images_containers_manifest.py

ENTRYPOINT /images_containers_manifest.py
