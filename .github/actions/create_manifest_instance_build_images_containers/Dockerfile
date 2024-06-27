FROM docker.io/library/python:3.12@sha256:fce9bc7648ef917a5ab67176cf1c7eb41b110452e259736144bc22f32f3aa622 AS builder

COPY images_containers_manifest.py /images_containers_manifest.py

ENTRYPOINT /images_containers_manifest.py
