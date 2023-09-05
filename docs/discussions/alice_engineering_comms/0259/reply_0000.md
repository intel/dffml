- https://github.com/ChristopherHX/github-act-runner
- https://gitea.com/gitea/act_runner/issues/35#issuecomment-732340

```console
$ gh extension install https://github.com/nektos/gh-act
$ gh act -W .github/workflows/pin_downstream.yml --env TEST_PIN_TO_COMMIT=$(git log -1 --format='%H') --env https_proxy=$HTTPS_PROXY --env http_proxy=$HTTP_PROXY --env no_proxy=$NO_PROXY
```

- https://github.com/repository-service-tuf/repository-service-tuf
  - https://repository-service-tuf.readthedocs.io/en/latest/guide/introduction/introduction.html
- https://github.com/keylime
- https://github.com/bigcode-project/starcoder
- TODO
  - [ ] https://github.com/intel/dffml/pull/1454
    - ActivityPub will facilitate results communication via https://github.com/soda480/wait-for-message-action/blob/main/README.md