# Usage
# docker build -t dffml/deploy .
# docker run --rm -ti -p 80:8080 dffml/deploy -insecure -log debug
#
FROM ubuntu:22.04@sha256:6042500cf4b44023ea1894effe7890666b0c5c7871ed83a97c36c76ae560bb9b

RUN apt-get update && \
  apt-get install -y \
    gcc \
    python3-dev \
    python3-pip \
    python3 \
    ca-certificates && \
  python3 -m pip install -U pip && \
  python3 -m pip install dffml-service-http && \
  apt-get purge -y \
    gcc \
    python3-dev && \
  rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
COPY . /usr/src/app

RUN python3 -m pip install -e .[dev]

ENTRYPOINT ["python3", "-m", "dffml", "service", "http", "server", "-addr", "0.0.0.0"]
CMD ["-mc-config", "deploy/deploy"]
