- instance always on chadig tcb forgejo workflow cve bin tool exec log ad hoc cves as issues use scitt and linked data to map. Finish stream of consciousness doc (federation is telepathy section in this chapter) policy engine angle? Later for embedded when ditch git for lfs style refs as manifests to registry.
- scitt for nahdig
- Scitt for chadig
- Guac as firewall, directus as insert and update graphql into guac db from workflow id’d agents or worflows. Also setup registry for each forge. OIDC all to forgejo. DO scripting from infra branch
- `cve-bin-tool --fix --fix-strategy URN-of-workflow-or-shorthand`
  - Start with two `--fix-strategy` and docs same as parsers PR
    - llm
    - workflow / policy engine exec
- `cve-bin-tool --fix --fix-with-vex --fix-with-vex-strategy`
  - Start with two `--fix-with-vex-strategy` and docs same as parsers PR
    - vexctl commit
    - workflow / policy engine exec

```bash
cat > Caddyfile <<'EOF'
{
  admin "unix//home/alice/caddy.admin.sock" {
    origins localhost
  }
}
EOF
sudo setcap cap_net_bind_service=+ep /usr/bin/caddy
sudo su alice -c 'caddy run --config Caddyfile'

curl -X POST --unix-socket /home/alice/caddy.admin.sock http://localhost/config/ -H 'Content-Type: application/json' -d "$(curl --unix-socket /home/alice/caddy.admin.sock http://localhost/adapt      -H "Content-Type: text/caddyfile"       --data-binary "$(echo -e 'git.pdxjohnny.localhost {\n    reverse_proxy /home/alice/git.pdxjohnny.localhost.sock\n}\n' | caddy fmt -)" | jq .result)"
```


- https://caddyserver.com/docs/automatic-https#local-https