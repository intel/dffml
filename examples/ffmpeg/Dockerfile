FROM alpine

RUN apk --no-cache add musl-dev python3-dev python3 gcc ffmpeg && \
  python3 -m pip install -U pip && \
  python3 -m pip install dffml-service-http && \
  python3 -m pip install dffml-config-yaml && \
  apk del musl-dev python3-dev gcc

WORKDIR /usr/src/app
COPY . /usr/src/app

RUN python3 -m pip install -e .

EXPOSE 8080

ENTRYPOINT ["python3", "-m", "dffml", "service", "http","server","-addr", "0.0.0.0","-insecure"]
CMD ["-mc-config", "deploy"]
# CMD /bin/sh
# python3 -m dffml service http server -addr 0.0.0.0 -insecure -mc-config deploy
