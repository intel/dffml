## 2023-11-07 @pdxjohnny Engineering Logs

- https://github.com/intel/cve-bin-tool/blob/main/.github/dependabot.yml
- https://github.com/scitt-community/scitt-examples/blob/cc337ba382ff126a1412d2658d1023162ed4ae81/python/script.sh
- https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-pypi
- Example SBOM upload to ORAS and hash to SCITT
  - https://scitt-community.github.io/scitt-api-emulator/registration_policies.html
  - https://oras.land
  - https://scitt.io
- Start the a container registry were we will store artifacts, we store references to artifacts within SCITT

```bash
docker run -d -p 5000:5000 --name oras-quickstart-registry ghcr.io/project-zot/zot-linux-amd64:latest
```

- Generate or download an SBOM
  - https://github.com/advanced-security/gh-sbom
    - `gh ext install advanced-security/gh-sbom`

```bash
export REPO_URL="https://github.com/intel/cve-bin-tool"
export REPO_ORG="$(echo ${REPO_URL} | sed -e 's/https:\/\/github.com\///g' | sed -e 's/\/.*//g')"
export REPO_NAME="$(echo ${REPO_URL} | sed -e 's/.*\///g')"
export TARGET_FILE="${REPO_NAME}.sbom.json"
gh sbom -r "${REPO_URL}" | python -m json.tool --sort-keys > "${TARGET_FILE}"
# echo "intel/cve-bin-tool/sbom/cve-bin-tool-py3.10.json" | xargs -I '{}' bash -ec 'export REPO_URL="{}" && mkdir -p files/$(dirname ${REPO_URL}) && export REPO_ORG=$(echo ${REPO_URL} | sed -e "s/\/.*//g") && export REPO_NAME=$(echo ${REPO_URL} | sed -e "s/${REPO_ORG}\///" | sed -e "s/\/.*//g") && export FILEPATH=$(echo ${REPO_URL} | sed -e "s/${REPO_ORG}\/${REPO_NAME}\///g") && gh api -H "Accept: application/vnd.github.raw" /repos/${REPO_ORG}/${REPO_NAME}/contents/${FILEPATH} > files/${REPO_ORG}/${REPO_NAME}/${FILEPATH}'
```

- Upload the contents of the SBOM to the registry

```bash
export REGISTRY_DOMAIN="localhost:5000"
export REGISTRY_USERNAME="$(python -m keyring get $USER registry.username)"
export REGISTRY_PASSWORD="$(python -m keyring get $USER registry.password)"
export REGISTRY_PROJECT="sbom"
export IMAGE_NAME="${REPO_ORG}-${REPO_NAME}"
export TARGET_RELEASE_TAG=$(gh -R "${REPO_URL}" release list -L 1 | awk '{print $(NF-1)}')
export TARGET_RELEASE_COMMIT=$(git ls-remote "${REPO_URL}" --tags "${TARGET_RELEASE}" | awk '{print $1}')
export IMAGE="${REGISTRY_DOMAIN}/${REGISTRY_PROJECT}/${IMAGE_NAME}:${TARGET_RELEASE_COMMIT}"
oras push -u "${REGISTRY_USERNAME}" -p "${REGISTRY_PASSWORD}" \
  "${IMAGE}" \
  "${TARGET_FILE}:application/json"
# Uploading 291a64cd275f cve-bin-tool.sbom.json
# Uploaded  291a64cd275f cve-bin-tool.sbom.json
# Pushed [registry] localhost:5000/sbom/intel-cve-bin-tool:92d27dceac8a7719b906892f253c035c86b4bfd6
# Digest: sha256:ad729afe0436d86e7f4672c06e9765f9a35c1415abac6fecddd4b0fbca9837e8
export IMAGE="${REGISTRY_DOMAIN}/${REGISTRY_PROJECT}/${IMAGE_NAME}:${TARGET_RELEASE_TAG}"
oras push -u "${REGISTRY_USERNAME}" -p "${REGISTRY_PASSWORD}" \
  "${IMAGE}" \
  "${TARGET_FILE}:application/json"
# Pushed [registry] localhost:5000/sbom/intel-cve-bin-tool:v3.2.1
# Digest: sha256:ad729afe0436d86e7f4672c06e9765f9a35c1415abac6fecddd4b0fbca9837e8
```

- Upload content address of SBOM to SCITT

```bash
scitt-emulator client create-claim --issuer TODO_CWT_ISSUER --content-type application/json --payload "{\"sbom\": {\"oci_image\": \"${IMAGE}\"}}" --out claim.cose
python -m cbor2.tool claim.cose
# {"CBORTag:18": ["\\xa3\u0001&\u0003papplication/json\u0019\u0001\\x87oTODO_CWT_ISSUER", {}, "{\"sbom\": {\"oci_image\": \"localhost:5000/sbom/intel-cve-bin-tool:v3.2.1\"}}", "~\\xe9\\xf7y\\x8e\\xa0\\xd8\\xea5琄\\x92VJ8_\\x86\\xf2\\xd8Y\\x91qDQ\r\\xd4\\xcc[\\xd9\u001dF&\\xd5\\xcc(\\x92hrj$\\x9c\u0019\\xf3\\xb7\u0001S\\x95@;\\xf1\\x88(bF32\u000f\\xfb\\x84\\xf1\\x809"]}
# A COSE signed Claim was written to:  claim.cose
scitt-emulator client submit-claim --claim claim.cose --out claim.receipt.cbor
# Example with OIDC Auth
# References
# - https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect#updating-your-actions-for-oidc
# OIDC_TOKEN=$(curl -H "Authorization: bearer $ACTIONS_ID_TOKEN_REQUEST_TOKEN" "$ACTIONS_ID_TOKEN_REQUEST_URL&audience=https://scitt.example.org")
# scitt-emulator client submit-claim --claim claim.cose --out claim.receipt.cbor --url https://scitt.example.org --cacert "${REQUESTS_CA_BUNDLE}" --token "${OIDC_TOKEN}"
# Claim registered with entry ID 1
# Receipt written to claim.receipt.cbor
python -m cbor2.tool claim.receipt.cbor
# ["\\xa3jservice_idhemulatorhtree_algcCCFiissued_at\u001aeJ^t", ["\\xc6\u0013uj\\x90\\x9a&\\xa1tūo\\xbcb\\xf1\u000fX\\x89\\xb7q[\\x84ڴ#Sr\u0018ߠMv\u001d\\xa4\\xd7\\xcaS=P\\xba\\xe8\\x90䗱\\xb5\tYsĝh\\xb9\\xbc\\x9d\\x83t\\x9bj\\x8a)\\xc8vk", "0\\x82\u0001 0\\x81Ǡ\u0003\u0002\u0001\u0002\u0002\u0014\u001f\\x9e^&u\\xfc\\xa4\u0011\\xf1\\xa10q@\\xdc\u0002J\u0016\\xe5\\x9d0\n\u0006\b*\\x86H\\xce=\u0004\u0003\u00020\u00121\u00100\u000e\u0006\u0003U\u0004\u0003\f\u0007service0\u001e\u0017\r231107155714Z\u0017\r241106155714Z0\u000f1\r0\u000b\u0006\u0003U\u0004\u0003\f\u0004node0Y0\u0013\u0006\u0007*\\x86H\\xce=\u0002\u0001\u0006\b*\\x86H\\xce=\u0003\u0001\u0007\u0003B\u0000\u0004P\u001d' pa\\xda\\xc1Qdj\\x9b_\\xe17\u00138\\xf4\\x8e\\x81\\xcc=\\xbc\\xe1\u0012\\xb6\\xd3\\xe6\\xb5\n\u001e\\xfeP\\xda\\xf1\\x9c\u001a?]\\xa6<\\xb1\\x93\\xa5\\xb5)k$\u0004\\xe3_\\x80j\\xb9\f\\xe5\\xe8\\xbbՍ\u00030\\xbb\b0\n\u0006\b*\\x86H\\xce=\u0004\u0003\u0002\u0003H\u00000E\u0002!\u0000\\xea\\xbc\b\\xfdM\\xa9\\x93\\xdbRn/d\u0002\u0017\\xe7\\x9b\\xf3\u0006\u0000\\xa8\\xd7̤\u000b\\xc2\\xc7:v%)h\\xb0\u0002 <\u0005\\xad\\xed\\xc4Ʈy\u0012\\xff\\xee\\x96I\\xf8Qz\\xb2\u001a\u000e\\xc51\\xe7\\xb6ژo\\xe7y\\xa6X\u0007\\xdd", [[true, "\\xd3F\\xc1/n\bf!n\\x87\\xa3\\xf8D\\x84\\xebsմ\t\u000f\\xccD\\xf7O\u0000b\\xa1\\xe2\u0015Rp\\xe4"], [true, "(|\\x90\\xae\\xabϘ\u0004\u001c\\x8c\u0015\r\\xa4d\\x81\u0002\\xa8\u0000\\x80W\u0010b\\x9cW:D\u0004S\\xe2K\\xf6\\x86"], [true, "ڔޏ\\xc1\\xa6i\u0013x\\xc9d\u0006\\x91\\xef\\xfbw\\x92\\x8e\u0016t\\xd1\n\\xc37cQ\u0016\\xd7jS\u001af"], [true, "p\\xa2\\xd6\u0013\\xa4\\x9b\\xb4\\xed2ɔ\\x9e\\xa36`\u000b7\u001b=\r\\xea\\xc9g\\xa7\u001e\\xb1\\xa6-\\xe8.\\xb0"], [true, "\\xb4\u0011\\xde\\xd0\u0012\\xae\\xb3\u001d\\xbf\u0000\\xf8'\\xc6\u0011ᴾ\u00198X\\xa4\u0012\\x8c,�L>\\x99\\xadČ"], [true, "9ܖ\\x86\u001dV\\xb3\\xd1\\\u000f\u0017u\u0001_8\\xec%Ֆ\\xff?\u0011Ď\\xd5y\u0013\u0001#\\xef\\xa6\\xc2"]], ["\\xb5\\xa2\\xc9bPa#f\\xea'/\\xfa\\xc6\\xd9tJ\\xafKE\\xaa͖\\xaa|\\xfc\\xb91\\xee;U\\x82Y", "1"]]]
```

- Example container build from `manifest.json`
  - https://github.com/intel/dffml/blob/156e8a91a46cbe7e9467d5d93204065107f1469e/schema/github/actions/build/images/containers/0.0.0.schema.json

**scitt-api-emulator.manifest.json**

```json
{
  "branch": "main",
  "build_args": "[[\"key0\", \"value0\"], [\"key1\", \"value1\"]]",
  "commit": "72a75511d7840d4062741185ec6879b585ee8c07",
  "dockerfile": "FROM python:3.11\nWORKDIR /usr/src/scitt-api-emulator\nRUN set -x && export KEYRING=/usr/share/keyrings/nodesource.gpg && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource.gpg.key | gpg --dearmor | tee \"$KEYRING\" >/dev/null && gpg --no-default-keyring --keyring \"$KEYRING\" --list-keys && chmod a+r /usr/share/keyrings/nodesource.gpg && . /usr/lib/os-release && export VERSION=node_20.x && export DISTRO=\"${VERSION_CODENAME}\" && echo \"deb [signed-by=$KEYRING] https://deb.nodesource.com/$VERSION $DISTRO main\" | tee /etc/apt/sources.list.d/nodesource.list && echo \"deb-src [signed-by=$KEYRING] https://deb.nodesource.com/$VERSION $DISTRO main\" | tee -a /etc/apt/sources.list.d/nodesource.list && apt-get update -y && apt-get install -y nodejs jq && rm -rf /var/apt/lists/* && mkdir -vp /opt/nodemon && cd /opt/nodemon && npm install nodemon && echo 'export PATH=$PATH:/opt/nodemon/node_modules/.bin' >> ~/.bashrc\nENV PATH=\"/opt/nodemon/node_modules/.bin:$PATH\"\nCOPY setup.py ./\nRUN pip install --no-cache-dir -e .[oidc,federation-activitypub-bovine]\nCOPY . .\nRUN pip install --no-cache-dir -e .[oidc,federation-activitypub-bovine]\nCMD scitt-emulator server --workspace workspace/ --tree-alg CCF --middleware scitt_emulator.federation_activitypub_bovine:SCITTFederationActivityPubBovine --middleware-config-path federation_workspace/config.json",
  "image_name": "scitt-api-emulator",
  "owner": "scitt-community",
  "repository": "scitt-api-emulator"
}
```

- Extract the dockerfile from the manifest to edit it

```bash
cat scitt-api-emulator.manifest.json | jq -r '.dockerfile' | tee scitt-api-emulator.Dockerfile
```

- Update the manifest with the content of the dockerfile

```bash
export manifest="$(cat scitt-api-emulator.manifest.json)" && dockerfile="$(cat scitt-api-emulator.Dockerfile)" jq -r '.dockerfile = env.dockerfile' <(echo "${manifest}") | tee scitt-api-emulator.manifest.json
```

- Export environment variables corresponding to JSON file keys

```bash
export manifest="$(cat scitt-api-emulator.manifest.json)"
export owner="$(jq -r -n 'env.manifest | fromjson | .owner')"
export repository="$(jq -r -n 'env.manifest | fromjson | .repository')"
export branch="$(jq -r -n 'env.manifest | fromjson | .branch')"
export commit="$(jq -r -n 'env.manifest | fromjson | .commit')"
export dockerfile="$(jq -r -n 'env.manifest | fromjson | .dockerfile')"
export image_name="$(jq -r -n 'env.manifest | fromjson | .image_name')"
unset build_args
declare -a build_args
while IFS=$'\n' read -r line; do
  build_args[${#build_args[@]}]="--build-arg"
  build_args[${#build_args[@]}]="${line}"
done < <(jq -n -r '[env.manifest | fromjson | .build_args | fromjson | .[] | (.[0] + "=" + .[1])] | join("\n")')
```

- Build the container image from the manifest

```bash
(set -x \
  && export tempdir="$(mktemp -d)" \
  && trap "rm -rf ${tempdir}" EXIT \
  && export TARGET_DIR="${tempdir}" \
  && export TARGET_REPO_URL="https://github.com/${owner}/${repository}" \
  && export TARGET_COMMIT="${commit}" \
  && mkdir -p "${TARGET_DIR}" \
  && cd "${TARGET_DIR}" \
  && git init \
  && git remote add origin "${TARGET_REPO_URL}" \
  && git fetch origin "${TARGET_COMMIT}" --depth 1 \
  && git reset --hard "${TARGET_COMMIT}" \
  && echo "${dockerfile}" | podman build --format docker --progress plain "${build_args[@]}" -t "${image_name}" -f - "${tempdir}")
```

- https://github.com/kcp-dev/kcp
  - CRD
  - GitHub org: dffml
  - Goal: Spin me #1401 repos based off YAML definition, hook them up to SCITT via webhook, give them some self hosted runners

```bash
skopeo copy docker://localhost:5000/ssh_public_keys/pdxjohnny dir:/tmp/ssh_public_keys
(
  for digest in $(cat /tmp/ssh_public_keys/manifest.json | jq -r '.layers[].digest'); do
    layer_tarball=${digest/sha256:/}
    tar -C /tmp/certs -xzvf /tmp/ssh_public_keys/${layer_tarball} --to-stdout --wildcards --no-anchored '*.pub'
  done
) > authorized_keys
```

- TODO
  - [ ] Ensure `build_arg` quoting works as intended
  - [ ] For CWT issuer derive key from SSH private key and resolve via github ssh keys endpoint
    - https://docs.github.com/en/rest/users/ssh-signing-keys?apiVersion=2022-11-28
    - https://github.com/pdxjohnny.keys
    - https://github.com/settings/keys