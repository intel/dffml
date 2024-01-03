## 2022-10-19 @pdxjohnny Engineering Logs

- https://twitter.com/Buntworthy/status/1582307817884889088
  - > Got Imagic running with Stable Diffusion, it's super easy to implement, will share a notebook soon! Left: Input image, Right: Edited "A photo of Barack Obama smiling big grin"
- https://twitter.com/prla/status/1582311844269543424
- https://twitter.com/krol_valencia/status/1582727276709679104
  - > Do you need Sbom, Sarif or vulnerability format? [#trivy](https://mobile.twitter.com/hashtag/trivy?src=hashtag_click)
    > - trivy image —format table alpine:3.10
    > - trivy image —format cyclonedx alpine:3.10
    > -  trivy image --format spdx-json alpine:3.10
    > - trivy image --format sarif alpine:3.10
    > - trivy image --format cosign-vuln alpine:3.10
- https://twitter.com/PrateekJainDev/status/1582717688652398592
  - > ![DED1BDCC-E701-4275-A218-575AAC3DF3FC](https://user-images.githubusercontent.com/5950433/196858876-b9c04512-2105-45fd-beb9-b04d2ae04816.jpeg)
- graph markov neural networks site:github.com offline rl
  - Terminal feedback loop, basic sysadmin stuff to start
  - https://github.com/ipld/js-dag-pb
  - https://github.com/ipld/js-dag-cbor
  - https://github.com/libp2p/js-libp2p-webrtc-star
- https://dweb.archive.org/details/home
- https://github.com/ipfs/js-ipfs/blob/master/docs/CONFIG.md
  - https://github.com/ipfs/js-ipfs/blob/master/docs/CONFIG.md#webrtcstar
  - https://github.com/libp2p/js-libp2p-floodsub
  - https://github.com/ipfs/js-ipfs/search?q=%3Aerror+TypeError%3A+fetch+failed&type=issues
    - https://github.com/ipfs/js-ipfs/issues/1481#issuecomment-410680460
    - https://github.com/multiformats/multiaddr/
    - https://github.com/ipfs/specs/blob/main/http-gateways/PATH_GATEWAY.md
    - https://github.com/ipfs/specs/blob/main/http-gateways/TRUSTLESS_GATEWAY.md

**init_config.json**

```json
{
    "Gateway": {
        "HTTPHeaders": {
            "Access-Control-Allow-Origin": [
                "http://pdxjohnny.devbox.nahdig.com:3000"
            ]
        }
    },
    "Addresses": {
        "API": "/ip4/0.0.0.0/tcp/5001",
        "Gateway": "/ip4/0.0.0.0/tcp/8080"
    }
}
```

```console
$ vim node_modules/ipfs-http-server/src/index.js
$ rm -rf /home/pdxjohnny/.jsipfs; DEBUG=ipfs:* ./node_modules/.bin/jsipfs daemon --enable-preload --init-profile server --init-config init_config.json 2>&1 | tee output.ipfs.daemon.$(date -Iseconds).txt
...
config
{
  Addresses: { API: 'http://0.0.0.0' },
  Discovery: {
    MDNS: { Enabled: true, Interval: 10 },
    webRTCStar: { Enabled: true }
  },
  Bootstrap: [],
  Pubsub: { Router: 'gossipsub', Enabled: true },
  Swarm: {
    ConnMgr: { LowWater: 50, HighWater: 200 },
    DisableNatPortMap: false
  },
  Routing: { Type: 'dhtclient' },
  Identity: {
    PeerID: '12D3KooWRunqtKfjPSHsF24iPdrxVQ2gnhBNtBMBKsz6zj6KoXTR',
    PrivKey: 'CAESQKlBi28qNtDDVusw/NmEUKEWQ+ZyfYto5ewCb4EtX2KW7x7LeH/arjGtMo8RRl8ydw0UU9uUlLKSJHA8zDS4PqQ='
  },
  Datastore: { Spec: { type: 'mount', mounts: [Array] } },
  Keychain: {
    DEK: {
      keyLength: 64,
      iterationCount: 10000,
      salt: 'vTamkostN5h+m+yAbevZDaF6',
      hash: 'sha2-512'
    }
  },
  Addressess: [ { info: [Object] } ]
}
headers
{}
apiAddrs
http://0.0.0.0
[1666206773378] INFO (3881696 on fedora-s-4vcpu-8gb-sfo3-01): server started
    created: 1666206773187
    started: 1666206773376
    host: "0.0.0.0"
    port: 43943
    protocol: "http"
    id: "fedora-s-4vcpu-8gb-sfo3-01:3881696:l9g0hqdf"
    uri: "http://0.0.0.0:43943"
    address: "0.0.0.0"
2022-10-19T19:12:53.448Z ipfs:http-api started
2022-10-19T19:12:53.448Z ipfs:http-gateway starting
2022-10-19T19:12:53.450Z ipfs:http-gateway started
2022-10-19T19:12:53.452Z ipfs:daemon started
js-ipfs version: 0.16.1
HTTP API listening on /ip4/0.0.0.0/tcp/43943/http
Web UI available at http://0.0.0.0:43943/webui
Daemon is ready
```

- Switching to Golang based IPFS implementation
  - https://github.com/ipfs/kubo
  - https://dweb.link/ipns/dist.ipfs.tech#kubo
    - https://docs.ipfs.tech/how-to/address-ipfs-on-web/#subdomain-gateway
- https://docs.ipfs.tech/how-to/command-line-quick-start/#take-your-node-online

```console
$ mkdir -p ~/.local
$ echo -e 'export PATH="${PATH}:${HOME}/.local/kubo"' | tee -a ~/.bashrc ~/.bash_profile
$ source ~/.bashrc
$ curl -sfL https://dist.ipfs.tech/kubo/v0.16.0/kubo_v0.16.0_linux-amd64.tar.gz | tar -C ~/.local -vxz
$ ipfs init --profile server
$ ipfs config Addresses.Gateway /ip4/0.0.0.0/tcp/8080
```

- http://pdxjohnny.devbox.nahdig.com:8080/ipfs/QmQ58yAN4oMsCZwhpHhfWPiFtBgSyxoVn2PFncnpuf5cBX
  - `I <3 IPFS -pdxjohnny`
  - SECURITY Gateway server is not supposed to be exposed

```
create:1 Access to XMLHttpRequest at 'http://pdxjohnny.devbox.nahdig.com:5001/api/v0/add?stream-channels=true&progress=false' from origin 'http://pdxjohnny.devbox.nahdig.com:3000' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
fetch.browser.js?273a:91          POST http://pdxjohnny.devbox.nahdig.com:5001/api/v0/add?stream-channels=true&progress=false net::ERR_FAILED 403
```

```console
$ ipfs config --help
$ ipfs daemon --help
$ ipfs config --json API.HTTPHeaders.Access-Control-Allow-Origin "[\"http://pdxjohnny.devbox.nahdig.com:3000\"]"
$ ipfs config --json API.HTTPHeaders.Access-Control-Allow-Methods "[\"PUT\", \"GET\", \"POST\"]"
$ ipfs config --json API.HTTPHeaders.Access-Control-Allow-Credentials "[\"true\"]"
$ ipfs daemon
$ curl 'http://pdxjohnny.devbox.nahdig.com:5001/api/v0/add?stream-channels=true&progress=false' \
  -H 'Accept: */*' \
  -H 'Accept-Language: en-US,en;q=0.9' \
  -H 'Connection: keep-alive' \
  -H 'Origin: http://pdxjohnny.devbox.nahdig.com:3000' \
  -H 'Referer: http://pdxjohnny.devbox.nahdig.com:3000/' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36' \
  -H 'content-type: multipart/form-data; boundary=-----------------------------eWfTjhbnBpWxbCcBUUJEX' \
  --data-raw $'-------------------------------eWfTjhbnBpWxbCcBUUJEX\r\nContent-Disposition: form-data; name="file"; filename=""\r\nContent-Type: application/octet-stream\r\n\r\nFILE_DATA\r\n-------------------------------eWfTjhbnBpWxbCcBUUJEX--\r\n' \
  --compressed \
  --insecure
```

- Try building static didme.me site and deploying from that
  - https://nextjs.org/docs/api-reference/cli#production

```console
$ npm install
$ NODE_OPTIONS=--openssl-legacy-provider npx next build
$ npx next start -p 3000
TypeError: Bolt URL expected to be string but was: undefined
$ git log -n 1
commit 14da8e47d8a1a4bef3cc1c85968c9f8b6963d269 (HEAD -> main, origin/main, origin/HEAD)
Author: Orie Steele <orie@transmute.industries>
Date:   Sun Jul 3 11:18:36 2022 -0500

    feat: ui/ux
```

```diff
diff --git a/core/NFT/NFT.ts b/core/NFT/NFT.ts
index 054d14c..eae5e76 100644
--- a/core/NFT/NFT.ts
+++ b/core/NFT/NFT.ts
@@ -18,6 +18,11 @@ export const getContract = async (web3: any) => {
 };

 export const getHistory = async (did: string) => {
+  return {
+    count: 0,
+    items: [],
+  };
+
   const {
     NEO4J_CONNECTION,
     NEO4J_USERNAME,
diff --git a/core/ipfs.ts b/core/ipfs.ts
index 44722cf..a6f8f40 100644
--- a/core/ipfs.ts
+++ b/core/ipfs.ts
@@ -4,28 +4,20 @@ const { urlSource } = ipfsHttpClient;
 const ipfsApis = [
   {
     label: "localhost",
-    url: "http://localhost:5001",
-  },
-  {
-    label: "infura",
-    url: "https://ipfs.infura.io:5001",
+    url: "http://pdxjohnny.devbox.nahdig.com:5001",
   },
 ];

 const ipfsGateways = [
   {
     label: "localhost",
-    url: "http://localhost:8080",
-  },
-  {
-    label: "infura",
-    url: "https://ipfs.infura.io",
+    url: "http://pdxjohnny.devbox.nahdig.com:8080",
   },
 ];

-const ipfsApi = ipfsApis[1].url;
+const ipfsApi = ipfsApis[0].url;

-const ipfsGateway = ipfsGateways[1].url;
+const ipfsGateway = ipfsGateways[0].url;

 const client = ipfsHttpClient({
   // url: "https://ipfs.infura.io:5001",
```

```console
$ python -c 'import sys, json, yaml; print(yaml.dump(json.loads(sys.stdin.read())))'
{"didDocument":{"@context":["https://www.w3.org/ns/did/v1","https://w3id.org/security/suites/jws-2020/v1"],"id":"did:meme:1zgsrnfgfe52zm0tgy4rgj0y5a3lnghmqduyv3yn8uw6tchfpzmxywuch7lza6","verificationMethod":[{"id":"did:meme:1zgsrnfgfe52zm0tgy4rgj0y5a3lnghmqduyv3yn8uw6tchfpzmxywuch7lza6#zQ3shrnCZq3R7vLvDeWQFnxz5HMKqP9JoiMonzYJB4TGYnftL","type":"JsonWebKey2020","controller":"did:meme:1zgsrnfgfe52zm0tgy4rgj0y5a3lnghmqduyv3yn8uw6tchfpzmxywuch7lza6","publicKeyJwk":{"kty":"EC","crv":"secp256k1","x":"tF8KQenSP2vPS3u-D5oLxwHOZEpSBcujQqGrysimK1E","y":"ZZB_Q4oHp3hboXCKYA_c5qEByYKAj2wXC9Rql6LO478"}}],"assertionMethod":["did:meme:1zgsrnfgfe52zm0tgy4rgj0y5a3lnghmqduyv3yn8uw6tchfpzmxywuch7lza6#zQ3shrnCZq3R7vLvDeWQFnxz5HMKqP9JoiMonzYJB4TGYnftL"],"authentication":["did:meme:1zgsrnfgfe52zm0tgy4rgj0y5a3lnghmqduyv3yn8uw6tchfpzmxywuch7lza6#zQ3shrnCZq3R7vLvDeWQFnxz5HMKqP9JoiMonzYJB4TGYnftL"],"capabilityInvocation":["did:meme:1zgsrnfgfe52zm0tgy4rgj0y5a3lnghmqduyv3yn8uw6tchfpzmxywuch7lza6#zQ3shrnCZq3R7vLvDeWQFnxz5HMKqP9JoiMonzYJB4TGYnftL"],"capabilityDelegation":["did:meme:1zgsrnfgfe52zm0tgy4rgj0y5a3lnghmqduyv3yn8uw6tchfpzmxywuch7lza6#zQ3shrnCZq3R7vLvDeWQFnxz5HMKqP9JoiMonzYJB4TGYnftL"],"keyAgreement":["did:meme:1zgsrnfgfe52zm0tgy4rgj0y5a3lnghmqduyv3yn8uw6tchfpzmxywuch7lza6#zQ3shrnCZq3R7vLvDeWQFnxz5HMKqP9JoiMonzYJB4TGYnftL"]},"didResolutionMetadata":{"didUrl":{"did":"did:meme:1zgsrnfgfe52zm0tgy4rgj0y5a3lnghmqduyv3yn8uw6tchfpzmxywuch7lza6","methodName":"meme","methodSpecificId":"1zgsrnfgfe52zm0tgy4rgj0y5a3lnghmqduyv3yn8uw6tchfpzmxywuch7lza6"}},"didDocumentMetadata":{"image":"http://pdxjohnny.devbox.nahdig.com:8080/ipfs/QmSDfug9jdkErKFvE1YHw44yestkppV92ae2qd4EuYHQxJ","ethereum":{"address":"0x30bB6577432a20d46b29Bd196997a8BA6b97C71b"},"bitcoin":{"address":"mh54xLL62pt5VXKmivS2JYBcv4qNWHJPPo"}}}
```

```yaml
didDocument:
  '@context':
  - https://www.w3.org/ns/did/v1
  - https://w3id.org/security/suites/jws-2020/v1
  assertionMethod:
  - did:meme:1zgsrnfgfe52zm0tgy4rgj0y5a3lnghmqduyv3yn8uw6tchfpzmxywuch7lza6#zQ3shrnCZq3R7vLvDeWQFnxz5HMKqP9JoiMonzYJB4TGYnftL
  authentication:
  - did:meme:1zgsrnfgfe52zm0tgy4rgj0y5a3lnghmqduyv3yn8uw6tchfpzmxywuch7lza6#zQ3shrnCZq3R7vLvDeWQFnxz5HMKqP9JoiMonzYJB4TGYnftL
  capabilityDelegation:
  - did:meme:1zgsrnfgfe52zm0tgy4rgj0y5a3lnghmqduyv3yn8uw6tchfpzmxywuch7lza6#zQ3shrnCZq3R7vLvDeWQFnxz5HMKqP9JoiMonzYJB4TGYnftL
  capabilityInvocation:
  - did:meme:1zgsrnfgfe52zm0tgy4rgj0y5a3lnghmqduyv3yn8uw6tchfpzmxywuch7lza6#zQ3shrnCZq3R7vLvDeWQFnxz5HMKqP9JoiMonzYJB4TGYnftL
  id: did:meme:1zgsrnfgfe52zm0tgy4rgj0y5a3lnghmqduyv3yn8uw6tchfpzmxywuch7lza6
  keyAgreement:
  - did:meme:1zgsrnfgfe52zm0tgy4rgj0y5a3lnghmqduyv3yn8uw6tchfpzmxywuch7lza6#zQ3shrnCZq3R7vLvDeWQFnxz5HMKqP9JoiMonzYJB4TGYnftL
  verificationMethod:
  - controller: did:meme:1zgsrnfgfe52zm0tgy4rgj0y5a3lnghmqduyv3yn8uw6tchfpzmxywuch7lza6
    id: did:meme:1zgsrnfgfe52zm0tgy4rgj0y5a3lnghmqduyv3yn8uw6tchfpzmxywuch7lza6#zQ3shrnCZq3R7vLvDeWQFnxz5HMKqP9JoiMonzYJB4TGYnftL
    publicKeyJwk:
      crv: secp256k1
      kty: EC
      x: tF8KQenSP2vPS3u-D5oLxwHOZEpSBcujQqGrysimK1E
      y: ZZB_Q4oHp3hboXCKYA_c5qEByYKAj2wXC9Rql6LO478
    type: JsonWebKey2020
didDocumentMetadata:
  bitcoin:
    address: mh54xLL62pt5VXKmivS2JYBcv4qNWHJPPo
  ethereum:
    address: '0x30bB6577432a20d46b29Bd196997a8BA6b97C71b'
  image: http://pdxjohnny.devbox.nahdig.com:8080/ipfs/QmSDfug9jdkErKFvE1YHw44yestkppV92ae2qd4EuYHQxJ
didResolutionMetadata:
  didUrl:
    did: did:meme:1zgsrnfgfe52zm0tgy4rgj0y5a3lnghmqduyv3yn8uw6tchfpzmxywuch7lza6
    methodName: meme
    methodSpecificId: 1zgsrnfgfe52zm0tgy4rgj0y5a3lnghmqduyv3yn8uw6tchfpzmxywuch7lza6
```

- 2022-04-17: f9d083fc0c99737f131601c1893b79a2c2907f2aa2a4bbe71ea3e4c237f8a51a
- fulcio issue DID (key)?
  - https://github.com/sigstore/fulcio/search?q=did
  - https://github.com/sigstore/fulcio/blob/fac62ed5e8fc7f4efa40c29ab8e1a5f1552f14bd/pkg/ca/tinkca/signer_test.go#L118
  - https://github.com/sigstore/fulcio/blob/fac62ed5e8fc7f4efa40c29ab8e1a5f1552f14bd/pkg/ca/tinkca/signer.go
  - https://github.com/sigstore/fulcio/blob/fac62ed5e8fc7f4efa40c29ab8e1a5f1552f14bd/pkg/ca/tinkca/signer.go#L46-L88
    - `new(ecdsapb.EcdsaPrivateKey)`
    - `new(ed25519pb.Ed25519PrivateKey)`
      - `ed25519.NewKeyFromSeed(privKey.GetKeyValue())`
      - https://github.com/intel/dffml/blob/alice/docs/arch/0007-A-GitHub-Public-Bey-and-TPM-Based-Supply-Chain-Security-Mitigation-Option.rst
      - https://twitter.com/pdxjohnny/status/1524535483396632576
      - https://twitter.com/pdxjohnny/status/1524870665764909056?s=20&t=z12dn9tVREZzK7huX6hsSg
  - By having fulcio also issue a DID for the attestation we can create dyanmic roots of trust associated with each manifest bom item queried later (at time of use)
    - We can export the public portion of the ephemeral DID key from fulcio and then use the DID key based method of verification of the doc contents offline / later
      - This also means it's easy to swap out BOM components, because we just swap out the key and did we verify against.
- Clicking around again

![image](https://user-images.githubusercontent.com/5950433/196825338-ad4f6933-8ee0-438d-911e-cb09aebe6c5f.png)

> ```console
> $ gh repo clone memes || gh repo create memes --template https://github.com/OR13/did-web-github-did-meme --public --clone
> $ cd memes && ./scripts/install.sh > did:meme:1zgsrnfgfe52zm0tgy4rgj0y5a3lnghmqduyv3yn8uw6tchfpzmxywuch7lza6
> ```

- https://or13.github.io/didme.me/did-method-spec.html
  - https://or13.github.io/didme.me/#using-github-pages
  - https://github.com/OR13/did-web-github-did-meme
  - https://identity.foundation/didcomm-messaging/spec/#out-of-band-messages
- Auth to fulcio issues Verifiable Credential
- Why are we doing this?
  - We want to not do risky things! risky things in this context are executions of system context which have negative impacts on strategic principles
  - We want to build Alice to be resilient to the open network
  - markov chain graph neural networks / offline rl
    - Trying to estimate what data to use, active learning, actively reevaluating chain of trust as they factor into the overall decision making process (gatekeeper and prioritizer)
    - We will issue DIDs and store provenance as VCs
      - This will allow us to trace provenance
      - We can then simulate good data / bad data situations
      - We will hopefully end up with models that develop strong security posture, i.e. are risk averse and good at getting the job done
- Just do the same thing with metric data instead of a meme! Duh…
- So for serialization we tranform the uuids on the inputs to their dids woth content uplod to digital ocean space and ipfs
- https://identity.foundation/keri/did_methods/
- https://or13.github.io/didme.me/did-method-spec.html
  - Let's try to modify this to use KERI DID method spec in place of DID key method spec

> ## DID Method Specification
>
> did:meme is a deterministic transformation of did:key, that uses IPFS, image content and bech32.
>
> ### DID Format
>
> ```
> did-meme-format := did:meme:<bech32-value>
> bech32-value    := [a-zA-HJ-NP-Z0-9]+
> ```
>
> The `bech32-value` is an encoded [multihash](https://multiformats.io/multihash/).
>
> The `multihash` is a content identifier for an image.
>
> The image contains a steganographically embedded `did:key`.
>
> See [did-key](https://w3c-ccg.github.io/did-method-key/#format).
>
> Another way of representing the `did:meme` identifier encoding:
>
> ```
> did:meme:<bech32(
>     multihash(
>         stego-embed(image, did:key)
>     )
> )>
> ```
>
> ### DID Operations
>
> See [did-key](https://w3c-ccg.github.io/did-method-key/#operations).
>
> #### Create
>
> - Generate a did:key
> - Steganographically embed the public key multicodec representation in a meme.
> - Upload the meme to ipfs.
> - Transform the CID to a did:meme with bech32.
> - Update the did document to use the did:meme identifier.
>
> #### Read
>
> - Convert the bech32 id to an ipfs CID.
> - Resolve the image.
> - Extract the did:key multicodec.
> - Construct the did:key document from the identifier.
> - Update the did document to use the did:meme identifier.
>
> #### Update
>
> Not supported.
>
> #### Deactivate
>
> Not supported.
>
> ### Security and Privacy Considerations
>
> See [did-key](https://w3c-ccg.github.io/did-method-key/#security-and-privacy-considerations)
>
> #### Security
>
> Because update and deactivate are not supported, did:meme should only be used for very short lived interactions, or just lulz.
>
> Because did:meme identifiers are a super set of did:key, it is possible for multiple did:meme to map to the same did:key… This can be problematic when private key compromise has occured.
>
> Generally speaking, did:meme has similar or weaker security properties compared with did:key.
>
> #### Privacy
>
>Be careful to strip XIF data or other meta data from images before constructing did:meme.
>
> Do not use images that identify physical locations or people.

- Community depth of field analysis
  - https://github.com/bumblefudge
    - Seems to be decentralized space leader
    - https://github.com/decentralized-identity/didcomm-messaging
    - https://github.com/decentralized-identity/schema-directory
    - https://github.com/centrehq/verite
    - https://github.com/learningproof/learningproof.github.io

---

Unsent to Hector with the city of portland’s open data effort.
Related: https://docs.google.com/document/d/1Ku6y50fY-ZktcUegeCnXLsksEWbaJZddZUxa9z1ehgY/edit
Related: https://github.com/intel/dffml/issues/1293

Hi Hector,

I wanted to circle back with you and see if there was anything you were aware of community effort wise involving city data and (de)centralized post disaster coordination efforts?

Thank you,
John