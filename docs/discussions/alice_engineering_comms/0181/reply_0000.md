## 2023-02-17 Engineering Logs

- https://github.com/amazon-science/mm-cot
- https://github.com/Nutlope/aicommits
- https://github.com/hpcaitech/ColossalAI
  - SCITT integreation
- https://mailarchive.ietf.org/arch/msg/scitt/zYC8SHJh-xO1NFGV4ltU8p6CLxo/
- https://github.com/oneapi-src/oneTBB
- https://github.com/oneapi-src/oneDPL
- One of the goals with the SCITT federation via ActivityPub is that it's a step towards the event stream being all JSONLD. Then audit and policy are effectively all done with definitions within DID referenced Verifiable Credentials. These encapsulate a receipt for a claim which who's insertion policy is a (or a context address of) policy as code aka compute contract. That contract statically defines or fulfils fetching or generating whatever data is needed to validate for insertion or federation and executes within a sandboxed environment. These policies can be overlayed with instance local additional policy as code. We can then read this event stream from anywhere or graft new trust chains off of it. GAUC is awesome it's just centralized from what I can tell, which is perfect for a performant view into a decentralized ecosystem. I think the two will work great together. We're all thinking in the same directions from what I can tell, just different goals in terms of data sovereignty, GUAC-GPT on the centralized side, Alice on the decentralized side.. The reason for the heavy focus on decentralization is that it for CI/CD we need to be able to spin dev and test chains of trust ad-hoc, for the AI side, we need to spin them for offline use cases tied to the users root of trust, or viewed as the user + their via hardware root of trust. Decentralized primitives allow us to never be forced to trust any authority other than what the deployment use case needs, scoping privilege to the threat model.
  - Introducing dependency on centralized transparency log infra creates a strategic choke point for trust.
    - Software defines everything, whoever controls what software is trusted effectively decides what is real, what is true. This is unacceptable.
      - https://hachyderm.io/@BlindMansBinary/109880611794898503
  - Do you control who you trust? Decentralized
    - ASAP target KERI SCITT for DICE interop
- https://docs.google.com/document/d/15Kb3I3SWhq-9_R7WYhSjsIxn_FykYgPyFlQWlLgF4fA/edit
- CVE Bin Tool policy based auto upgrade
  - SCITT insertion policy and federation
    - Cross with OpenSSF Metrics
      - Loop back with Ryan
  - This loops back to our `alice shouldi contribute`, for what deps we trust, use/no use
    - https://intel.github.io/dffml/main/examples/integration.html
- We want to propagate polices for recommending insertion
  - How do we know if it's worth propagating? We look at the lifecycle of usage of that recommendation, if track record of improvement in ecosystem, then we propigate trust of that policy (insersion policy, or depenednnecy we are recommending, same thing, recursive)
  - Easy to use and find
    - Make it easy to do the right thing
- Atomic habits
  - Make it easy to do what you need to do to get into the habit
    - This is about validating the PR before submitting it
- Not low friction, no friction
- If somehting has a proven track record of working functionally, or security, then we want to recommend it (OpenSSF Metrics)
- How do we decrecommended , make sure they run functionally on XYZ
- If we are going to recommened using a dependnecy we need to attempt a run using it to see if it works
  - It should work under stress of small, medium, large
    - Can Alice PR give you a package and push to SCITT action?
      - IDK, did you fork an try it Alice?
- Think about dev flow, similar to cve bin tool update, how do they nkow there is an update? How do they update with PIP and SCITT?
  - GO backwards from user install to vcs.push
- https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/uploading-a-sarif-file-to-github
- https://github.com/rqlite/rqlite
- https://github.com/rqlite/pyrqlite

**schema/image/container/build/activitypubstarterkit.json**

```json
{
    "$schema": "https://github.com/intel/dffml/raw/alice/schema/image/container/build/0.0.0.schema.json",
    "$format_name": "image.container.build",
    "include": [
        {
            "branch": "alternate_port",
            "build_args": "[[\"ACCOUNT\", \"testaccount\"]]",
            "commit": "ca92bfae5092bce908b70f6b5e0afbe242ce7a5b",
            "dockerfile": "activitypubstarterkit.Dockerfile",
            "image_name": "activitypubstarterkit",
            "owner": "jakelazaroff",
            "repository": "activitypub-starter-kit"
        }
    ]
}
```


```console
$ python -c 'import pathlib, json, sys; print(json.dumps({"manifest": json.dumps(json.loads(sys.stdin.read().strip())["include"])}))' < schema/image/container/build/activitypubstarterkit.json | gh -R intel/dffml workflow run dispatch_build_images_containers.yml --ref main --json
```

- https://github.com/jenkinsci/configuration-as-code-plugin/blob/master/docs/features/configExport.md
- https://identity.foundation/keri/did_methods/
  - https://github.com/microsoft/scitt-ccf-ledger
  - https://github.com/hyperledger-labs/private-data-objects
  - https://trustedcomputinggroup.org/wp-content/uploads/DICE-Layering-Architecture-r19_pub.pdf
    - From Ned: KERI controller as DICE layer/root of trust
- https://github.com/TBD54566975/dwn-aggregator
- https://github.com/TBD54566975/dwn-sdk-js
  - https://github.com/TBD54566975/dwn-sdk-js/releases/tag/v0.0.21
  - https://github.com/TBD54566975/dwn-sdk-js/pull/233
    - > * introduced DataStore as a peer interface to MessageStore
      > * refactored code such that MessageStoreLevel now has zero knowledge of data store
      > * refactored code such that there is no need to pass resolver, messageStore, and dataStore for every message handling call, this has been painful for a while especially when it comes to writing/refactoring tests
      > * kept MessageStore interface as untouched as possible to minimize scope of PR, but might want to add minor tweaks
      > * moved third party type definitions from devDependencies to dependencies as TypeScript projects are having trouble locating those dependencies on their own
- It's coming together
  - Ref early engineering logs, circa hyperledger firefly, we want to onramp data to the hypergraph via all angles, Fediverse -> DID & VC, secured via `did:keri:` + SCITT

![chaos_for_the_chaos_God](https://user-images.githubusercontent.com/5950433/219821754-e718904c-968f-4ed8-8e06-bba8b7d990bc.jpg)
