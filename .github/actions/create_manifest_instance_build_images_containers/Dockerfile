FROM docker.io/library/python:3.12@sha256:5a88c14f0f26df7a092edc139bdec35621e8ac11f8c95b38d2a9283bad0cfce1 AS builder

COPY images_containers_manifest.py /images_containers_manifest.py

ENTRYPOINT /images_containers_manifest.py
