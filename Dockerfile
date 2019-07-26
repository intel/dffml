FROM python:3.7

WORKDIR /usr/src/dffml

COPY . .
RUN pip install -U pip && \
  pip install --no-cache-dir . && \
  cp scripts/docker-entrypoint.sh /usr/bin/ && \
  chmod 755 /usr/bin/docker-entrypoint.sh

ENTRYPOINT ["/usr/bin/docker-entrypoint.sh"]
