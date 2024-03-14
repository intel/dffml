# Usage
# docker build -t $USER/ffmpeg .
# docker run --rm -ti -p 8080:8080 $USER/ffmpeg -mc-config deploy -insecure -log debug
#
# curl -v --request POST --data-binary @input.mp4 http://localhost:8080/ffmpeg -o output.gif
FROM ubuntu:22.04@sha256:a2bbdf79d03f6d4171bbd6ebb4782f6229375951987d3427ec3d9373f9841cd7

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
  apt-get install -y \
    gcc \
    python3-dev \
    python3-pip \
    python3 \
    ca-certificates \
    ffmpeg && \
  python3 -m pip install -U pip && \
  python3 -m pip install dffml-service-http && \
  python3 -m pip install dffml-config-yaml && \
  apt-get purge -y \
    gcc \
    python3-dev && \
  rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
COPY . /usr/src/app

ENTRYPOINT ["python3", "-m", "dffml", "service", "http", "server", "-addr", "0.0.0.0"]
CMD ["-mc-config", "deploy"]
