## 2023-05-26 @pdxjohnny Engineering Logs

- https://github.com/google/oss-fuzz/blob/9afbc7068fa0e88980c22229c6dbcdd60185414f/infra/base-images/base-builder/srcmap
- https://github.com/tacosframework/TACOS-spec
  - > TACOS is a framework for assessing the development practices of open source projects against a set of secure development standards specified in the NIST SSDF. The framework defines a machine-readable specification that can be used as a part of the overall self-attestation requirement to comply with the requirements and deadlines outlined in OMB memorandum M-22-18. 
- https://github.com/tacosframework/examples
- https://github.com/eugeneyan/open-llms
- https://github.com/salesforce/LAVIS
  - https://github.com/salesforce/LAVIS/blob/main/examples/blip2_instructed_generation.ipynb
- https://github.com/mozilla/sccache/blob/main/docs/Redis.md
- https://yaml-multiline.info/

```dockerfile
FROM dffml.registry.digitalocean.org/dffml as builder

RUN curl -fLO 'https://github.com/ChristopherHX/github-act-runner/releases/download/v0.6.2/binary-linux-amd64.tar.gz' \
  && sha384sum -c<<<'3ae3ee4df40392af65a5287019d26f895d7253455446c13ac945c39b0eb4beea20d24cf92658b3a2ccd3a33bf79a5a38  binary-linux-amd64.tar.gz' \
  && tar -xvf binary-linux-amd64.tar.gz \
  && rm -v config.sh run.sh binary-linux-amd64.tar.gz \
  && export LOCAL_PATH=$(echo $PATH | sed -e 's/:.*//g') \
  && mv github-act-runner "${LOCAL_PATH}/" \
  && du -h "${LOCAL_PATH}/github-act-runner"
```

```console
$ docker run --rm -ti -e OWNER_REPOSITORY="intel/dffml" -e TOKEN=$(grep oauth_token < ~/.config/gh/hosts.yml | sed -e 's/    oauth_token: //g') -e LABELS="github-act-runner-alice-shouldi-contribute" dffml.registry.digitalocean.org/github-act-runner-alice-shouldi-contribute bash -xc 'cleanup () { github-act-runner remove --force --unattended; }; github-act-runner configure   --url "https://github.com/${OWNER_REPOSITORY}"   --pat "${TOKEN}"   --name "container-$(hostname)"   --labels "${LABELS}"   --ephemeral   --unattended && trap cleanup EXIT && github-act-runner run'
```

- TODO
  - [ ] Add refs to TACOS within https://github.com/ietf-scitt/use-cases/pull/18
  - [ ] Get access to the Azure preview of TDX and run kata in it with the runners with rebuild chains, prophet