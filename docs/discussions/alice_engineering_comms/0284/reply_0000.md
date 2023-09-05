- https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/using-openid-connect-with-reusable-workflows#defining-the-trust-conditions
- #1242

```console
$ for i in $(seq 0 $(($(nproc) / 4))); do docker run -d --name=github-act-runner-alice-shouldi-contribute-$i --cpus 2 --restart=always -e OWNER_REPOSITORY="intel/dffml" -e TOKEN=$(grep oauth_token < ~/.config/gh/hosts.yml | sed -e 's/    oauth_token: //g') -e LABELS="github-act-runner-alice-shouldi-contribute" dffml.registry.digitalocean.org/github-act-runner-alice-shouldi-contribute; done
```

- https://openfl.readthedocs.io/en/latest/running_the_federation.html#aggregator-based-workflow
- https://www.intel.com/content/www/us/en/developer/articles/community/open-fl-project-improve-accessibility-for-devs.html
- https://lfaidata.foundation/blog/2023/03/09/intels-transition-of-openfl-primes-growth-of-confidential-ai/
- https://github.com/slsa-framework/slsa-verifier/issues/12
- https://github.com/slsa-framework/slsa-github-generator/blob/main/RENOVATE.md