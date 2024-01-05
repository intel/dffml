## 2023-11-23 @pdxjohnny Engineering Logs

- Happy Thanksgiving!

```bash
export COMPUTE_IPV4=$(doctl compute droplet list --no-header --format PublicIPv4 prophecy-0)
doctl compute domain records create --record-name alice --record-ttl 3600 --record-type A --record-data "${COMPUTE_IPV4}" chadig.com
doctl compute domain records create --record-name github-webhook-notary.scitt.alice --record-ttl 3600 --record-type A --record-data "${COMPUTE_IPV4}" chadig.com
ssh -nNT -R 127.0.0.1:7777:0.0.0.0:7777 alice@scitt.alice.chadig.com
```

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

scitt.unstable.chadig.com {
  reverse_proxy http://localhost:8000
}

scitt.pdxjohnny.chadig.com {
  reverse_proxy http://localhost:9000
}

define.chadig.com {
  respond "Cha-Dig: can you dig it? chaaaaaaa I can dig it!!!"
}
```

- Claus
  - https://www.scandinaviastandard.com/what-is-janteloven-the-law-of-jante/
- TODO
  - [ ] GitHub App Blueprints to
    - [x] https://github.com/apps/alice-oa
    - [ ] Webhook events to notarizing proxy
      - [ ] `$ gh webhook forward   --repo=intel/dffml   --events='*'   --url=https://github-webhook-notary.scitt.alice.chadig.com`
      - [ ] https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries#python-example
  - [ ] #1315
    - [ ] Bovine based downstream event receiver
    - [ ] As async iterator for new data events
  - [ ] POC using OpenAI agent threads with file uploads
    - [ ] Alice engineering log entry in daily discussion thread for updates
      - [ ] Checkbox checked by maintainer for requests approval
  - [ ] Assign issues to Alice via `Assignee: @aliceoa` watch webhook issue creation or body updates
    - `cat issues.action\:edited.json | jq 'select(.issue.body | index("Assignee: @aliceoa"))'`