## 2023-02-28 @pdxjohnny Engineering Logs

- https://github.com/anthonyharrison/sbom4python
  - For down the dependency rabbit hole again
- Down the dependency rabbit hole again as Dockerfile FROM extractor as asynciter to an output operation which returns a dataflow with all found dependencies (container image URI) as Inputs in seed
  - Another output operation which outputs the set/combo if needed of schema, `jq`, cypher, or open policy agent to yield true on evaluation of an incoming `vcs.push` (as schema URL with format name and version). This will be facilitating our kontain.me source only rebuild triggers.
  - Mock the push events by curl instead of websocket publishing to AcivityPub to test
    - This is the same way one would implement a pooling based proxy from web2
- https://github.com/facebookresearch/faiss/wiki/Getting-started
- https://github.com/facebookresearch/faiss/wiki/Running-on-GPUs
- https://github.com/facebookresearch/faiss/wiki/Index-IO,-cloning-and-hyper-parameter-tuning#example-usage
- Software DNA (in part based on the FROM image builds, the open architecture description, our methodology for traversal of the graph) encoded to vector representation (some encoding that yields similar images for similar aspects of the software lifecycle focused on).
- The wait for message on ActivityPub will enable our poly repo merge queue
- https://github.com/w3c-ccg/vc-api
- https://www.intel.com/content/www/us/en/developer/articles/technical/software-bills-of-materials-the-basics.html
- https://github.com/transmute-industries/example-mapping-from-jwt-to-jsonld
- ACDC is a way to secure a Credential
  - https://github.com/w3c/vc-data-model/issues/895#issuecomment-1434609248
  - https://github.com/w3c/vc-jwt/pull/56
  - https://github.com/w3c/vc-data-model/issues/947#issuecomment-1434506542
    - This transcript is important, see Orie's concerns about security. jsonld, nquads
  - https://github.com/ietf-scitt/statements-by-reference/pull/1
- https://github.com/libp2p/js-libp2p-websockets
- https://github.com/libp2p/js-libp2p-interfaces
- https://w3c.github.io/wot-scripting-api/#discovery-examples
- https://w3c.github.io/wot-scripting-api/#the-emitpropertychange-method
- https://www.chromium.org/teams/web-capabilities-fugu/
- https://github.com/gojue/ecapture
- For vsc.push source container proxy repackage (upstream into kontain.me)

```console
$ cd $(mktemp -d)
$ curl -L -H "Authorization: token $(grep oauth_token < ~/.config/gh/hosts.yml | sed -e 's/    oauth_token: //g')" -H "Accept:application/vnd.github.v3.raw" https://api.github.com/repos/intel/dffml/tarball/master | tar xvz
$ echo -e "FROM scratch\nCOPY ./$(ls) /src" > Dockerfile
$ docker build -t registry.example.org/dffml -f Dockerfile .
$ docker save registry.example.org/dffml | tar --extract --to-stdout --wildcards --no-anchored 'layer.tar' | tar --extract
```

- https://marquezproject.ai/quickstart
  - ActivityPub -> OpenLinage
- [RFCv2: IETF SCITT: Use Case: OpenSSF Metrics: activitypub extensions for security.txt](https://github.com/ietf-scitt/use-cases/blob/22afd537180d6c6b2d5ec4db0096f0706cb2b6bc/openssf_metrics.md)
  - It's basically a decentralized pubsub event notification methodology that can be done over ACDC piggybacking on ActivityPub as layer 7.
    - Event data lives "off chain" in a container registry secured via existing transparency service based methods (KERI, SCITT, SigStore), where the chain is the network of keys involved for a train of thoughts comms between entities. Since we transmit ActivityPub over KERI, the graph of our supply chain data we are sharing can be shared with trusted actors who agree not to be duplicitous, and who's KERI keys can be tied back to TEEs so that we can confirm they are running software that doesn't intend (via ML-based, Alice, analysis) to be duplicitous. We can now have our trusted computing based for decentralized compute, aka CI/CD pipelines delivering across project trust boundries.
  - Duplicity detection is a MUST have
    - Transparency services are just audit trails without this
      - DNS example from Sam: Multiple CAs can issue for the same domain. https://henkvancann.github.io/identifiers/keri-oobi.html
      - Revocation
        - OCSP Stapling
    - We add in the ActivityPub `Note`s and statues 
      - https://database.guide/what-is-acid-in-databases/
- https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository

![image](https://user-images.githubusercontent.com/5950433/222050628-40aadba8-8fc3-4d33-8603-f6391b37a7ad.png)

- https://github.com/decentralized-identity/keri/blob/master/kids/kid0001Comment.md#keri-message-parsing
- https://henkvancann.github.io/identifiers/cesr-one-of-sam-smiths-inventions-is-as-controversial-as-genius.html
- https://henkvancann.github.io/identifiers/cesr-proof-signatures-are-the-segwit-of-authentic-data-in-keri.html