## 2024-06-07 @pdxjohnny Engineering Logs

- https://github.com/livekit/livekit
  - WebRTC goodness in golang
- https://aeon.co/essays/for-over-a-century-telepathy-has-been-just-around-the-corner

```caddyfile
alice.chadig.com {
  redir "https://github.com/intel/dffml/discussions/1406?sort=new" temporary
}

github-webhook-notary.scitt.alice.chadig.com {
  reverse_proxy http://localhost:7777
}

scitt.bob.chadig.com {
  reverse_proxy http://localhost:6000
}

scitt.alice.chadig.com {
  reverse_proxy http://localhost:7000
}

view.scitt.unstable.chadig.com {
  reverse_proxy http://localhost:8001
}

scitt.unstable.chadig.com {
  reverse_proxy http://localhost:8000
}

scitt.pdxjohnny.chadig.com {
  reverse_proxy http://localhost:9000
}

git.pdxjohnny.chadig.com {
  reverse_proxy http://localhost:3000
}

forgejo.pdxjohnny.chadig.com {
  reverse_proxy http://localhost:3000
}

directus.pdxjohnny.chadig.com {
  reverse_proxy http://localhost:8055
}

define.chadig.com {
  respond "Cha-Dig: can you dig it? chaaaaaaa I can dig it!!!"
}
```

```bash
ssh -nNT -R 127.0.0.1:3000:0.0.0.0:3000 alice@scitt.unstable.chadig.com
ssh -nNT -R 127.0.0.1:8055:0.0.0.0:8055 alice@scitt.unstable.chadig.com
```

```bash
export FORGEJO_FQDN="git.pdxjohnny.chadig.com" \
&& export DIRECTUS_FQDN="directus.pdxjohnny.chadig.com" \
&& docker run \
  -ti \
  --rm \
  -p 8055:8055 \
  -e PUBLIC_URL="https://${DIRECTUS_FQDN}" \
  -e AUTH_DISABLE_DEFAULT=true \
  -e AUTH_PROVIDERS="forgejo" \
  -e AUTH_FORGEJO_DRIVER="openid" \
  -e AUTH_FORGEJO_CLIENT_ID="$(python -m keyring get directus auth.forgejo.client_id)" \
  -e AUTH_FORGEJO_CLIENT_SECRET="$(python -m keyring get directus auth.forgejo.client_secret)" \
  -e AUTH_FORGEJO_ISSUER_URL="https://${FORGEJO_FQDN}/.well-known/openid-configuration" \
  -e AUTH_FORGEJO_IDENTIFIER_KEY="email" \
  -e AUTH_FORGEJO_REDIRECT_ALLOW_LIST="https://${DIRECTUS_FQDN}/auth/login/forgejo/callback" \
  -e AUTH_FORGEJO_ALLOW_PUBLIC_REGISTRATION=true \
  -e AUTH_FORGEJO_DEFAULT_ROLE_ID="855add86-04b0-4074-93ed-3be14c14479c" \
  -e SECRET="$(head -n 99999 /dev/urandom | sha384sum - | awk '{print $1}')" \
  directus/directus
```

- It looks like forgejo is requesting /auth/login/forgejo

```
[22:31:36] GET /auth/login/forgejo?redirect=https%3A%2F%2Fdirectus.pdxjohnny.chadig.com%2Fadmin%2Flogin%3Freason%3DUNKNOWN_EXCEPTION%26continue%3D 302 15ms
[22:31:37] GET /auth/login/forgejo/callback?code=gta_wk3wjw2esyee2wkkzmaaccgrnacsxfdenzzkyj3pcaopd22iq22q&state=9OeOAbvzUIvYrkoLXUGN5u6BQams6uT8yTCvowYzrdg 302 512ms
[22:31:36.586] WARN: [OAuth2] Unknown error
    err: {
      "type": "TypeError",
      "message": "only valid absolute URLs can be requested",
      "stack":
          TypeError: only valid absolute URLs can be requested
              at Client.request (/directus/node_modules/.pnpm/openid-client@5.6.5/node_modules/openid-client/lib/helpers/request.js:71:11)
              at Client.authenticatedPost (/directus/node_modules/.pnpm/openid-client@5.6.5/node_modules/openid-client/lib/helpers/client.js:187:18)
              at async Client.grant (/directus/node_modules/.pnpm/openid-client@5.6.5/node_modules/openid-client/lib/client.js:1343:22)
              at async Client.oauthCallback (/directus/node_modules/.pnpm/openid-client@5.6.5/node_modules/openid-client/lib/client.js:620:24)
              at async OAuth2AuthDriver.getUserID (file:///directus/node_modules/.pnpm/@directus+api@file+api_@aws-sdk+client-sso-oidc@3.569.0_@aws-sdk+client-sts@3.569.0_@types+no_crtpmuhomzjtudzfxjp6matirq/node_modules/@directus/api/dist/auth/drivers/oauth2.js:100:24)
              at async AuthenticationService.login (file:///directus/node_modules/.pnpm/@directus+api@file+api_@aws-sdk+client-sso-oidc@3.569.0_@aws-sdk+client-sts@3.569.0_@types+no_crtpmuhomzjtudzfxjp6matirq/node_modules/@directus/api/dist/services/authentication.js:44:22)
              at async file:///directus/node_modules/.pnpm/@directus+api@file+api_@aws-sdk+client-sso-oidc@3.569.0_@aws-sdk+client-sts@3.569.0_@types+no_crtpmuhomzjtudzfxjp6matirq/node_modules/@directus/api/dist/auth/drivers/oauth2.js:272:28
    }
[22:31:37.085] WARN: [OAuth2] Unexpected error during OAuth2 login
    err: {
      "type": "TypeError",
      "message": "only valid absolute URLs can be requested",
      "stack":
          TypeError: only valid absolute URLs can be requested
              at Client.request (/directus/node_modules/.pnpm/openid-client@5.6.5/node_modules/openid-client/lib/helpers/request.js:71:11)
              at Client.authenticatedPost (/directus/node_modules/.pnpm/openid-client@5.6.5/node_modules/openid-client/lib/helpers/client.js:187:18)
              at async Client.grant (/directus/node_modules/.pnpm/openid-client@5.6.5/node_modules/openid-client/lib/client.js:1343:22)
              at async Client.oauthCallback (/directus/node_modules/.pnpm/openid-client@5.6.5/node_modules/openid-client/lib/client.js:620:24)
              at async OAuth2AuthDriver.getUserID (file:///directus/node_modules/.pnpm/@directus+api@file+api_@aws-sdk+client-sso-oidc@3.569.0_@aws-sdk+client-sts@3.569.0_@types+no_crtpmuhomzjtudzfxjp6matirq/node_modules/@directus/api/dist/auth/drivers/oauth2.js:100:24)
              at async AuthenticationService.login (file:///directus/node_modules/.pnpm/@directus+api@file+api_@aws-sdk+client-sso-oidc@3.569.0_@aws-sdk+client-sts@3.569.0_@types+no_crtpmuhomzjtudzfxjp6matirq/node_modules/@directus/api/dist/services/authentication.js:44:22)
              at async file:///directus/node_modules/.pnpm/@directus+api@file+api_@aws-sdk+client-sso-oidc@3.569.0_@aws-sdk+client-sts@3.569.0_@types+no_crtpmuhomzjtudzfxjp6matirq/node_modules/@directus/api/dist/auth/drivers/oauth2.js:272:28
    }
[22:31:37] GET /admin/login?reason=UNKNOWN_EXCEPTION 304 2ms
[22:31:37] GET /extensions/sources/index.js 200 10ms
[22:31:37] POST /auth/refresh 400 10ms
[22:31:38] GET /auth?sessionOnly 304 10ms
[22:31:38] GET /server/info 304 12ms
[22:31:38] GET /translations?fields[]=language&fields[]=key&fields[]=value&filter[language][_eq]=en-US&limit=-1 403 10ms
[22:38:55] GET / 302 3ms
[22:38:56] GET /admin 200 4ms
[22:38:56] GET / 302 1ms
[22:38:56] GET /admin 200 1ms
[22:38:57] GET /favicon.ico 404 14ms
[22:38:58] GET / 302 1ms
[22:38:58] GET /admin 200 1ms
[22:38:59] GET / 302 1ms
[22:38:59] GET /admin 200 2ms
```

- https://python-keycloak.readthedocs.io/en/latest/reference/keycloak/keycloak_admin/index.html#keycloak.keycloak_admin.KeycloakAdmin.create_realm
  - https://www.keycloak.org/docs-api/24.0.2/rest-api/index.html#RealmRepresentation
- https://python-keycloak.readthedocs.io/en/latest/reference/keycloak/keycloak_admin/index.html#keycloak.keycloak_admin.KeycloakAdmin.create_realm_role
  - https://www.keycloak.org/docs-api/24.0.2/rest-api/index.html#RoleRepresentation
- https://python-keycloak.readthedocs.io/en/latest/_modules/keycloak/keycloak_admin.html#KeycloakAdmin.create_user
  - https://www.keycloak.org/docs-api/24.0.2/rest-api/index.html#_userrepresentation
- https://www.keycloak.org/docs-api/24.0.2/rest-api/openapi.json
- https://github.com/pdxjohnny/dotfiles/blob/cabd91401ad65e87dba076d9e12c53384c82b71e/keycloak_init.py

[![asciicast](https://asciinema.org/a/663076.svg)](https://asciinema.org/a/663076)

- https://gist.github.com/pdxjohnny/d9c9a4e5b4dc2804be6bb0a93d524b3f

![image](https://github.com/intel/dffml/assets/5950433/791d873c-fccb-410c-acb0-4b1626bf27d1)

[![asciicast](https://asciinema.org/a/663082.svg)](https://asciinema.org/a/663082)

- https://git.pdxjohnny.chadig.com/.well-known/openid-configuration

```json
{
    "issuer": "https://git.pdxjohnny.chadig.com/",
    "authorization_endpoint": "https://git.pdxjohnny.chadig.com/login/oauth/authorize",
    "token_endpoint": "https://git.pdxjohnny.chadig.com/login/oauth/access_token",
    "jwks_uri": "https://git.pdxjohnny.chadig.com/login/oauth/keys",
    "userinfo_endpoint": "https://git.pdxjohnny.chadig.com/login/oauth/userinfo",
    "introspection_endpoint": "https://git.pdxjohnny.chadig.com/login/oauth/introspect",
    "response_types_supported": [
        "code",
        "id_token"
    ],
    "id_token_signing_alg_values_supported": [
        "RS256"
    ],
    "subject_types_supported": [
        "public"
    ],
    "scopes_supported": [
        "openid",
        "profile",
        "email",
        "groups"
    ],
    "claims_supported": [
        "aud",
        "exp",
        "iat",
        "iss",
        "sub",
        "name",
        "preferred_username",
        "profile",
        "picture",
        "website",
        "locale",
        "updated_at",
        "email",
        "email_verified",
        "groups"
    ],
    "code_challenge_methods_supported": [
        "plain",
        "S256"
    ],
    "grant_types_supported": [
        "authorization_code",
        "refresh_token"
    ]
}
```

- https://docs.directus.io/contributing/running-locally.html

```bash
--entrypoint sh -v "${HOME}/.local/admin_role_id.txt:${HOME}/directus_admin_role_id.txt:ro" -v "${HOME}/.local/directus.sqlite3:${HOME}/database/database.sqlite:rw"

set -x && node cli.js bootstrap && while [ ! -f admin_role_id.txt ]; do sleep 0.01; done && export AUTH_FORGEJO_DEFAULT_ROLE_ID=$(cat admin_role_id.txt) && pm2-runtime start ecosystem.config.cjs
```

- TODO
  - [ ] `AUTH_FORGEJO_DEFAULT_ROLE_ID="855add86-04b0-4074-93ed-3be14c14479c"`
  - [ ] Copy caddytls certs for these domains and `/etc/hosts` them so that offline and online dev are the same
    - [ ] Use tricks.md DO scripts as base for auto spin up and spin down and DNS for this stack, deploy using k8s
      - [ ] Future expand to multi node deployment and abstraction around CSP
  - [ ] LangGraph workflow for this OpenAPI + language bindings poly repo flow we've been in with keycloak-python and openapi. This would help us write idiomatic clients.
    - [ ] Expand this with the prioritizer juggling scheduling of background trains of thought to re-explore or continue exploration of adjacent trains of thought to any known trains of thought.