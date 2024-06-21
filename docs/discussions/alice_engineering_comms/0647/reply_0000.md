## 2024-06-06 @pdxjohnny Engineering Logs

- https://github.com/directus/directus
  - #1400
- GitHub custom properties are world readable
- https://henryjacksonsociety.org/publications/lessons-from-the-first-cyberwar-how-supporting-ukraine-on-the-digital-battlefield-can-help-improve-the-uks-online-resilience/
- https://docs.directus.io/self-hosted/config-options.html#file-storage
  - `STORAGE_LOCATIONS`
    - > A CSV of storage locations (e.g., local,[digitalocean](https://pdxjohnny.github.io/tricks/#digital-ocean),amazon) to use. You can use any names you'd like for these keys.
      - https://github.com/s3fs-fuse/s3fs-fuse
        - https://docs.digitalocean.com/reference/api/spaces-api/
          - DO doesn't do event notifications
- https://docs.directus.io/self-hosted/sso-examples.html#keycloak
- https://github.com/pdxjohnny/pdxjohnny/discussions/1
- https://forgejo.org/download/
- https://github.com/go-gitea/gitea/issues/3816
- https://github.com/go-gitea/gitea/issues/5482#issuecomment-491940322

```bash
GITEA_WORK_DIR=$HOME/.local/appdata forgejo web
```

- [x] http://localhost:3000/.well-known/openid-configuration

```json
{
    "issuer": "http://localhost:3000/",
    "authorization_endpoint": "http://localhost:3000/login/oauth/authorize",
    "token_endpoint": "http://localhost:3000/login/oauth/access_token",
    "jwks_uri": "http://localhost:3000/login/oauth/keys",
    "userinfo_endpoint": "http://localhost:3000/login/oauth/userinfo",
    "introspection_endpoint": "http://localhost:3000/login/oauth/introspect",
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

[![asciicast](https://asciinema.org/a/662966.svg)](https://asciinema.org/a/662966)

- https://docs.directus.io/self-hosted/sso-examples.html#github
- http://localhost:3000/admin/applications/oauth2
- https://github.com/directus/directus/blob/b5c4c6dc7c65af75a7e1e8d9cba5e1cdc2b1901e/docs/self-hosted/sso.md?plain=1#L61
  - > 3. On **Authorized redirect URIs** put your Directus instance address plus `/auth/login/google/callback`. For example, you should put
    > `https://directus.myserver.com/auth/login/google/callback` where
    > `https://directus.myserver.com` should be the address of your Directus instance.
    > If you are testing locally you should add
    > `http://localhost:8055/auth/login/google/callback` too

![image](https://github.com/intel/dffml/assets/5950433/301aedad-bb8a-4745-bca1-133eb941c399)

```bash
echo AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA | python -m keyring set directus auth.forgejo.client_id
echo 'AAA_AAAAAAAAAA' | python -m keyring set directus auth.forgejo.client_secret
```

- https://docs.directus.io/getting-started/quickstart.html

```bash
export HOST_IP="$(ip address show docker0 | grep inet | awk '{print $2}' | sed -e 's/\/.*//g')" && \
echo 'using --net host so localhost' && \
export HOST_IP="localhost" && \
docker run \
  -ti \
  --rm \
  -p 8055:8055 \
  -e AUTH_FORGEJO_REDIRECT_ALLOW_LIST="http://localhost:8055/auth/login/forgejo" \
  -e AUTH_FORGEJO_DRIVER="oauth2" \
  -e AUTH_FORGEJO_AUTHORIZE_URL="http://${HOST_IP}:3000/login/oauth/authorize" \
  -e AUTH_FORGEJO_ACCESS_URL="https://${HOST_IP}:3000/login/oauth/access_token" \
    -e AUTH_FORGEJO_PROFILE_URL="https://${HOST_IP}:3000/api/user" \
    -e AUTH_FORGEJO_CLIENT_ID="$(python -m keyring get directus auth.forgejo.client_id)" \
    -e AUTH_FORGEJO_CLIENT_SECRET="$(python -m keyring get directus auth.forgejo.client_secret)" \
  -e AUTH_PROVIDERS="forgejo" \
  -e AUTH_DISABLE_DEFAULT=true \
  -e PUBLIC_URL=https://localhost:3000 \
  -e AUTH_FOREGOJO_ALLOW_PUBLIC_REGISTRATION=true \
  --net host \
  -e SECRET="$(head -n 99999 /dev/urandom | sha384sum - | awk '{print $1}')" \
  directus/directus
```

[![asciicast](https://asciinema.org/a/662976.svg)](https://asciinema.org/a/662976)

- TODO
  - [ ] Why is it insecure to bind `0.0.0.0`? 
    - We should bind to UNIX sockets when possible or the loopback if not (127.0.0.1). Anyone on your local network scan connect to `0.0.0.0`.