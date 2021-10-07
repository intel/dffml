FROM alpine
# Certs are needed to talk to Let's Encrypt ACME resolver
RUN apk --no-cache add ca-certificates curl tar grep sed && \
  latest=$(curl -sSL https://github.com/caddyserver/caddy/releases | grep _linux_amd64.tar.gz | head -n 1 | sed -e 's/.*download\///g' -e 's/".*//g') && \
  curl -L "https://github.com//caddyserver/caddy/releases/download/${latest}" | tar -xvz -C /usr/bin && \
  apk --no-cache del curl tar grep sed
ENV CADDYPATH /.cert
CMD ["/usr/bin/caddy", "-conf", "/Caddyfile", "-agree", "-email", "johnandersenpdx@gmail.com"]
