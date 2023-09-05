## 2023-03-01 @pdxjohnny Engineering Logs

- https://github.com/stefanbuck/github-issue-parser
- https://codeberg.org/openEngiadina/geopub#semantic-social-network
- OpenFL integration for ActivitSecurity txt event stream engest
- https://socialhub.activitypub.rocks/t/standardizing-on-activitypub-groups/1984
  - We can aggregate data from individual push accounts deployed into a group which puts that data under the correct thread for it's schema.

```console
$ while [ ! -f stop ]; do FDQN=vcs.activitypub.securitytxt.dffml.chadig.com WEBHOOK_PATH=$(cat ../webhook) NODE_ENV=production PORT=8000 ACCOUNT=push ADMIN_USERNAME=admin ADMIN_PASSWORD=$(cat ../password) PUBLIC_KEY=$(cat publickey.crt) PRIVATE_KEY=$(cat pkcs8.key) npm run start; done
```

- GitHub Issue based fork + exec
  - Add YAML manifests for overlays

```console
$ echo -e "### We created a new plugin, the GitHub repo is\nhttps://github.com/dffml/dffml-model-transformers" | gh issue create -R https://github.com/intel/dffml --title "plugin: new: dffml-model-transformers" --body-file /dev/stdin
$ jq -r -n 'env.BUILD_ARGS' | jq '. |= . + [["APPEND", env.APPEND]]'
```

- TODO
  - [ ] #1061
    - [ ] Model transformers downstream watcher
      - [ ] ramfs to limit sqlite
      - [ ] systemd unit files to start
  - [x] Meet with Yash
  - [x] https://github.com/jakelazaroff/activitypub-starter-kit/blob/fcd5942485d86a66913c5554f85ae905785504e0/src/admin.ts#L54
    - [e642b406f68f747586a05ed07f9fc247ed6c02e8](https://github.com/jakelazaroff/activitypub-starter-kit/commit/e642b406f68f747586a05ed07f9fc247ed6c02e8)
  - [ ] https://github.com/actions/runner/issues/2417