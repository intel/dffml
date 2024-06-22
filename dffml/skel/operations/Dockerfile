# Usage
# docker build -t REPLACE_ORG_NAME/REPLACE_IMPORT_PACKAGE_NAME .
# docker run --rm -ti -p 80:8080 REPLACE_ORG_NAME/REPLACE_IMPORT_PACKAGE_NAME  -insecure -log debug
#
# curl -v http://127.0.0.1:80/list/sources
FROM ubuntu:24.04@sha256:562456a05a0dbd62a671c1854868862a4687bf979a96d48ae8e766642cd911e8

RUN apt-get update && \
  apt-get install -y \
    gcc \
    python3-dev \
    python3-pip \
    python3 \
    ca-certificates && \
  python3 -m pip install -U pip==24.1 --hash=sha256:a775837439bf5da2c1a0c2fa43d5744854497c689ddbd9344cf3ea6d00598540 --hash=sha256:bdae551038c0ce6a83030b4aedef27fc95f0daa683593fea22fa05e55ed8e317 && \
  python3 -m pip install dffml-service-http==0.1.0.post0 --hash=sha256:27f1fdfdc560c6b9266a5657b9ad6b69d9b7da0acf1bd4b6a1317bd1c5c31bae --hash=sha256:a0e252836a36323156d191c535952210f263c47e1d00523f6993d1812f00fcfe && \
  apt-get purge -y \
    gcc \
    python3-dev && \
  rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
COPY . /usr/src/app

RUN python3 -m pip install -e .[dev]

ENTRYPOINT ["python3", "-m", "dffml", "service", "http", "server", "-addr", "0.0.0.0"]
CMD ["-mc-config", "REPLACE_IMPORT_PACKAGE_NAME/deploy"]
