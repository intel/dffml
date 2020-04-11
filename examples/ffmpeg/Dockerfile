FROM alpine

RUN apk --no-cache add musl-dev python3-dev python3 gcc && \
  python3 -m pip install -U pip && \
  python3 -m pip install dffml-service-http && \
  apk del musl-dev python3-dev gcc

WORKDIR /usr/src/app
COPY . /usr/src/app

RUN python3 -m pip install -e .

EXPOSE 8000

ENTRYPOINT ["python3", "-m", "dffml", "service", "http"]
CMD ["server","insecure","-mc-config", "deploy"]

