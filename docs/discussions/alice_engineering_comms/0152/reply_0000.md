## 2023-01-19 @pdxjohnny Engineering Logs

- Ask terri if cve-bin-tool got integrated into [Trivy](https://github.com/aquasecurity/trivy)
- Soon we'll be able to talk to Alice like a ⁠[rubber duck](https://en.wikipedia.org/wiki/Rubber_duck_debugging) @mepsheehan
  - https://github.com/enhuiz/vall-e
  - https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_architecting_alice/0004_writing_the_wave.md
- https://github.com/facebookresearch/esm#quickstart
  - For our software DNA
- https://learn.microsoft.com/en-us/windows/wsl/wsl-config#systemd-support
- https://github.com/intel/dffml/commit/73f13854a637a505a4dde3b82a0399192a8563cd
- Need a way to trigger downstream on container pushed
  - https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#create-a-repository-dispatch-event
  - https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#repository_dispatch
  - kontain.me style registry but supporting push as a proxy for upload elsewhere, use OA to implement dynamic sandboxed hooks to upload to other endpoints, possibly attested compute to enable client secrets #1247
    - https://github.com/imjasonh/kontain.me/tree/main/cmd/buildpack
- https://gist.github.com/pdxjohnny/a0dc3a58b4651dc3761bee65a198a80d#file-run-vm-sh-L148-L167
- Realized multi-stage builds allow for removal of `ARG` from published layers
  - Docker builds provide native cross platform caching for CI jobs, they just need downstream trigger support
- https://github.com/TBD54566975/dwn-sdk-js/blob/58656ed4f881b8a0e746cd34650174a267f605d7/tests/utils/test-data-generator.ts#L307-L330
  - Ideally this would facilitate the downstream validation on registry webhook upload (or other) event
- https://fosstodon.org/@kernellogger/109717087722762476
  - https://lore.kernel.org/all/Y8lSYBU9q5fjs7jS@T590/
  - https://gist.github.com/pdxjohnny/07b8c7b4a9e05579921aa3cc8aed4866#file-rolling_alice_progress_report_0011_september_activities_recap-md
    - Now we can run everything in gvisor, kaniko, and image builds, and build VMs via  usermode ndb for the loopback (or did we end up going with packer?)
- Harbor has webhooks and OIDC auth support
  - > OIDC support: Harbor leverages OpenID Connect (OIDC) to verify the identity of users authenticated by an external authorization server or identity provider. Single sign-on can be enabled to log into the Harbor portal.
  - Digital Ocean does not have webhook notifications on image upload events at time of writing (or any webhook config for registries)
  - https://github.com/dexidp/dex supported
  - https://github.com/aquasecurity/trivy supported

![image](https://user-images.githubusercontent.com/5950433/213610588-1f0e5edf-53bc-4c3d-9655-509c5eb8198c.png)

**Dockerfile**

```dockerfile
FROM docker.io/intel-otc/dffml as builder

ARG GH_ACCESS_TOKEN
ARG ORG=intel
ARG REPO_NAME=dffml

# Configure auth
RUN mkdir -p ~/.config/gh/ \
  && echo "github.com:" > ~/.config/gh/hosts.yml \
  && echo "    oauth_token: ${GH_ACCESS_TOKEN}" >> ~/.config/gh/hosts.yml \
  && echo "    user: ${GH_USER}" >> ~/.config/gh/hosts.yml \
  && echo "    git_protocol: https" >> ~/.config/gh/hosts.yml \
  && gh auth setup-git

# Change to location of cached tools directory
WORKDIR /src/dffml/entities/alice

# Run scan
# Remove secrets from output via sed and stream output to tee to write to file
# - GH_ACCESS_TOKEN
RUN export REPO_URL="https://github.com/${ORG}/${REPO_NAME}" \
  && python -m alice shouldi contribute -log debug -keys "${REPO_URL}" \
  && export ORIGINAL_JSON_SOURCE_OUTPUT=".tools/open-architecture/innersource/repos.json" \
  && mkdir -p output \
  && cat "${ORIGINAL_JSON_SOURCE_OUTPUT}" \
     | python -m json.tool \
     | sed \
       -e "s/${GH_ACCESS_TOKEN}@//g" \
       -e "s/${GH_ACCESS_TOKEN}/\$GH_ACCESS_TOKEN/g" \
     | tee output/result.json \
     | python -c 'import yaml, json, sys; print(yaml.dump(json.load(sys.stdin)))' \
     | tee output/result.yaml

FROM scratch

COPY --from=builder /src/dffml/entities/alice/output /
```

```console
$ export REGISTRY=docker.io
$ export IMAGE=scan-non-existent
$ export GH_ACCESS_TOKEN=$(grep oauth_token < ~/.config/gh/hosts.yml | sed -e 's/    oauth_token: //g')
$ tar cz Dockerfile | docker build --build-arg=GH_ACCESS_TOKEN --build-arg=ORG=intel --build-arg=REPO_NAME=non-existent -f Dockerfile -t "${REGISTRY}/${IMAGE}" -
$ docker push "${REGISTRY}/${IMAGE}"
$ reg manifest -u "${REG_USERNAME}" -p "${REG_PASSWORD}" "${REGISTRY}/${IMAGE}"
```

```json
{
   "schemaVersion": 2,
   "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
   "config": {
     "mediaType": "application/vnd.docker.container.image.v1+json",
     "size": 234,
     "digest": "sha256:0019f2f429283f393e6280210b81f6763df429fd50bb25805f6c60bc09013cf5"
   },
   "layers": [
     {
       "mediaType": "application/vnd.docker.image.rootfs.diff.tar.gzip",
       "size": 512,
       "digest": "sha256:f4215bb8acc2c4822edb2ae9c748c2e855d4e4c8ff3ce972867bef1da3c122c5"
     }
   ]
}
```

```console
$ DIGEST=$(reg manifest -u "${REG_USERNAME}" -p "${REG_PASSWORD}" "${REGISTRY}/${IMAGE} \
    | grep digest \
    | head -n 2 \
    | tail -n 1 \
    | sed -e 's/.*sha/sha/' -e 's/"//g')
$ reg layer -u "${REG_USERNAME}" -p "${REG_PASSWORD}" "${REGISTRY}/${IMAGE}@${DIGEST}" | tar xzv
tar: Removing leading `/' from member names
/
schema.json
result.json
result.yaml
$ cat result.yml
$ reg layer -u "${REG_USERNAME}" -p "${REG_PASSWORD}" "${REGISTRY}/${IMAGE}@${DIGEST}" | tar xzO result.yaml
```

```yaml
untagged:
  https://github.com/intel/non-existent:
    extra: {}
    features:
      ActionsValidatorBinary: []
      CodeNarcServerProc: []
      JavaBinary: []
      NPMGroovyLintCMD: []
      URL: []
      date:
      - 2023-01-19 11:00
      date_pair:
      - - 2023-01-19 11:00
        - 2022-10-19 11:00
      quarter: []
      quarter_start_date: []
      str: []
      valid_git_repository_URL: []
    key: https://github.com/intel/non-existent
    last_updated: '2023-01-19T11:00:42Z
```

- Base32 SSH key

```console
$ tempdir=$(mktemp -d); ssh-keygen -b 4096 -f "${tempdir}/html_scp_deploy_key" -P "" \
  && python -c 'import sys, base64; print(base64.b32encode(sys.stdin.read().encode()).decode())' < $tempdir/html_scp_deploy_key  \
    | python -c 'import sys, base64; print(base64.b32decode(sys.stdin.read().strip().encode()).decode(), end="")' \
    | tee $tempdir/out \
  && chmod 600 $tempdir/out  \
  && ssh-keygen -y -f $tempdir/out
```

- TODO
  - [ ] SLSA3 via sigstore examples
  - [ ] Use `/manifest.json|*` to embed manifest used to build container (stripped approriatly) into results scratch, this way downstream "validation" (conversion to correct storage location, perhaps transformation into proper ORSA.land) can decide how it should handle the contents
    - Use #1273