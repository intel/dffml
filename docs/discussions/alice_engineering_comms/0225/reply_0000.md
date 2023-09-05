## 2023-04-01 @pdxjohnny Engineering Logs

- SCITT hits DWN in deno or aureascript / or SSI Service.
  - Client Accept: helps SCITT decide if it needs to create a VC. If in federated mode it always creates so that DWN SSI can do comms (yeet example dwn).
  - Maintain entry id to claim contemt mapping service to help clients check for emtry / request recepts if they retrive content or receive content and need to verify. This will allow them to take releaseasset.json and take its content address (hash of blob too) and request recipt for it from other forge via DWN/SSI Service.
- Bob's forge bulids a package
  - Bob's forge uploads package and SBOM to oras.land
  - Bob's forge creates a releaseasset.json event with a SCITT receipt as a Verifiable Credential
    - We don't have to do the eventing/federation yet between forges be
- SGX runner save load git/heartwood repo workspace for hacky federation of that
  - Ideally add the routes to SCITT or have SCITT watch the DWN/SSI Service yeeter
- https://github.com/TBD54566975/dwn-sdk-js/blob/096908798a649ffd9292e38295a1b95f8df73ba7/tests/interfaces/records/handlers/records-write.spec.ts#L575-L727
  - Most recent commit, Let's goooooooooooooooooooooooooooooo!
- https://github.com/TBD54566975/dwn-sdk-js/blob/0bd41a18bb8654be6039cc06c4999e1809fe8277/tests/vectors/protocol-definitions/social-media.json
- https://github.com/TBD54566975/dwn-sdk-js/pull/290
  - https://github.com/TBD54566975/dwn-sdk-js/issues/14
  - https://github.com/TBD54566975/incubating-web5-labs/commit/7376f6ec7232d910f34d2c2a75e833e7e63b091b#commitcomment-106278196
  - https://github.com/TBD54566975/incubating-web5-labs/pull/24

![chaos-for-the-chaos-god](https://user-images.githubusercontent.com/5950433/220794351-4611804a-ac72-47aa-8954-cdb3c10d6a5b.jpg)

- `did:keri` issuer insert policy could check if stack is booted from TEE which existes in transpranecy service via claim content
  - Turtles all the way down
    - 🐢🐢🐢🐢🐢🐢🐢🐢
- Related issues to insert policy by `job_workflow_sha` + `repositoryUri` + `repository_id` OIDC SCITT notary
  - https://github.com/actions/runner/issues/458
  - https://github.com/actions/runner/issues/2473
  - https://github.com/actions/runner/issues/2417
- https://intel.github.io/dffml/main/examples/shouldi.html#bandit-operation
- https://deno.land/manual@v1.32.2/node/how_to_with_npm/redis
- https://deno.land/manual@v1.32.2/node/how_to_with_npm/apollo
- https://deno.land/manual@v1.32.2/examples/module_metadata
- https://deno.land/manual@v1.32.2/examples/chat_app
- https://deno.land/manual@v1.32.2/advanced/typescript/configuration#using-the-lib-property
- https://github.com/TBD54566975/dwn-sdk-js/blob/0bd41a18bb8654be6039cc06c4999e1809fe8277/tests/vectors/protocol-definitions/credential-issuance.json
- https://github.com/TBD54566975/dwn-sdk-js/blob/0bd41a18bb8654be6039cc06c4999e1809fe8277/tests/vectors/protocol-definitions/dex.json
  - Compute contract negotiation
  - Vuln submission
  - Pull requests on pull requests until accepted
- Updated description of https://github.com/ietf-scitt/use-cases/pull/18
  - Title: Use Case: Attestations of alignment to S2C2F and org specific overlays
  - Related: https://github.com/ietf-scitt/use-cases/issues/14
  - Related: https://github.com/ossf/s2c2f/blob/main/specification/framework.md#appendix-relation-to-scitt
  - Collection of metric data into shared database (crowdsourcable OpenSSF Metrics).
There are many repos to search, we want to enable self reporting and granularity
as applicable to ad-hoc formed policy as desired by end-user. We want this to
work across fully decentrailized, federated, and central forges/factories.
  - This use case will be mostly focused on the policy / gatekeeper component and federation components of [SCITT](https://datatracker.ietf.org/doc/draft-ietf-scitt-architecture/).
    - 5.2.2: Registration Policies
    - 7: Federation
  - This use case is a specialization of (cross between) the following use cases from the [Detailed Software Supply Chain Uses Cases for SCITT](https://datatracker.ietf.org/doc/draft-ietf-scitt-software-use-cases/) doc.
    - 3.3: Security Analysis of a Software Product
      - We'll cover OpenSSF Scorecard and other analysis mechanisms including meta static analysis / aggregation (example: GUAC).
    - 3.4: Promotion of a Software Component by multiple entities
      - We'll cover how these entities can leverage analysis mechanisms to achieve feature and bugfix equilibrium across the diverged environment.
        - Future use cases could explore semantic patching to patch across functionally similar
- Known policy violations
  - Recursive SCITT
  - Submit original to trusted
    - Denied
      - Inspect response
  - Submit each violation using open architecture doc within policy denial response of "questionable" SCITT(s)
  - Resubmit with receipts for each violation
    - Insert
- Our OpenSSF metrics SCITT use case will provide automated decision making and transparency required for automl with auto feature enginering.
- TODO
  - [x] Sleep
  - [x] Stare at the Sun
  - [ ] CVE Bin Tool triage patchset to enable checking triage exceptions with scitt
  - [ ] CVE Bin Tool GitHub Action with post step that uploads to SCITT if SBOM in location
    - https://github.com/actions/setup-python/blob/181184007f6fb1dd659dccd4a04b6e145680b052/src/cache-save.ts
    - https://github.com/actions/setup-python/blob/181184007f6fb1dd659dccd4a04b6e145680b052/action.yml#L39
    - https://docs.github.com/en/actions/creating-actions/creating-a-javascript-action
  - [x] [Implement reason communication associated with policy enforcement](https://github.com/scitt-community/scitt-api-emulator/pull/27/commits/a72cdefab4e97368bccd1ec4aab0ef4c65d8b061)
    - Now we can begin to have a conversation about what needs changing.
      - Alice and Bob both run SCITT instances. Alice will requires sign off receipts from Eve on each claim he submits to her instance which doesn't adhear to upstream policy (default OpenSSF Scorecard set).