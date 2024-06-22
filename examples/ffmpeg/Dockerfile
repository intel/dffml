# Usage
# docker build -t $USER/ffmpeg .
# docker run --rm -ti -p 8080:8080 $USER/ffmpeg -mc-config deploy -insecure -log debug
#
# curl -v --request POST --data-binary @input.mp4 http://localhost:8080/ffmpeg -o output.gif
FROM ubuntu:24.04@sha256:562456a05a0dbd62a671c1854868862a4687bf979a96d48ae8e766642cd911e8

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
  apt-get install -y \
    gcc \
    python3-dev \
    python3-pip \
    python3 \
    ca-certificates \
    ffmpeg && \
  python3 -m pip install -U pip==24.1 --hash=sha256:a775837439bf5da2c1a0c2fa43d5744854497c689ddbd9344cf3ea6d00598540 --hash=sha256:bdae551038c0ce6a83030b4aedef27fc95f0daa683593fea22fa05e55ed8e317 && \
  python3 -m pip install dffml-service-http==0.1.0.post0 --hash=sha256:27f1fdfdc560c6b9266a5657b9ad6b69d9b7da0acf1bd4b6a1317bd1c5c31bae --hash=sha256:a0e252836a36323156d191c535952210f263c47e1d00523f6993d1812f00fcfe && \
  python3 -m pip install dffml-config-yaml==0.1.0.post0 --hash=sha256:8bf1f365da282bc3d9a3c3a660ac45916fc8b997c2e526daef2e862b49a3b6ad --hash=sha256:918e209c66f405a659d7ad7e6a5c678f472539e3ca2c537c9781e49d564c4d62 && \
  apt-get purge -y \
    gcc \
    python3-dev && \
  rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
COPY . /usr/src/app

ENTRYPOINT ["python3", "-m", "dffml", "service", "http", "server", "-addr", "0.0.0.0"]
CMD ["-mc-config", "deploy"]
