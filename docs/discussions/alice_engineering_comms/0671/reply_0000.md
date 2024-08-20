- https://github.com/caddyserver/caddy/commit/68c5c71659109b10226f10873f7dc67102b9dc14
- https://github.com/mindsdb/mindsdb/issues/9024
  - https://github.com/mindsdb/mindsdb/pull/9032
- https://github.com/pdxjohnny/caddy-oidc-auth

```bash
xcaddy build --with github.com/pdxjohnny/caddy-oidc-auth
sudo setcap cap_net_bind_service=+ep /usr/bin/caddy
```