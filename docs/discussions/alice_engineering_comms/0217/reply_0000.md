## 2023-03-23 @pdxjohnny Engineering Logs

- [/me](https://user-images.githubusercontent.com/5950433/227560451-033923b3-52ff-4d4b-8be3-7cd14ab2a62d.jpeg) bolts out of bed in the 4 o'clock hour with a sudden urge
  - Must... investigate... traceability-interop....
    - https://github.com/w3c-ccg/traceability-interop/tree/main/docs/tutorials
    - https://github.com/w3c-ccg/traceability-interop/tree/main/docs/tutorials/authentication
      - Have been avoiding this because postman... but whatever
- https://w3c-ccg.github.io/traceability-interop/draft/#software-supply-chain
- Discovered that typing `/` in a markdown field on GitHub opens a quick markdown formatting helper
  - ![image](https://user-images.githubusercontent.com/5950433/227520416-1f285044-ef2e-4303-9575-d0ec5ea3c2e1.png)
- We're trying to bridge the current world of comms (fast becoming ActivityPub) to the new world (Web5 `did:keri:`)
  - If we make progress we'll post `![knowledge-graphs-for-the-knowledge-god](https://user-images.githubusercontent.com/5950433/222981558-0b50593a-c83f-4c6c-9aff-1b553403eac7.png)`
  - ![image](https://user-images.githubusercontent.com/5950433/227520859-7213f415-e371-4780-927d-01228f89873a.png)
    - https://github.com/pdxjohnny/pdxjohnny.github.io/blob/3e642942d5ef1a48a3bab3c1bc65dc91182e1f7d/data/saved_replies_markdown.yaml
- https://www.postman.com/downloads/
  - > `Postman CLI\nNew!`
    - I was avoiding postman because I didn't want to use a GUI, yay!
      - https://pdxjohnny.github.io/dev-environment/
        - https://github.com/intel/dffml/pull/1207#discussion_r1036680987
          - The reason for the meticulousness of engineering log documentation.
            We must have reproducible process for Alice to follow.

![chaos-for-the-chaos-god](https://user-images.githubusercontent.com/5950433/220794351-4611804a-ac72-47aa-8954-cdb3c10d6a5b.jpg) 

- Chaos for the Chaos God again apparently from the postman team as we `curl | sh` + sudo

```console
$ curl -o- "https://dl-cli.pstmn.io/install/linux64.sh" | sh
```

- https://learning.postman.com/docs/postman-cli/postman-cli-options/
- https://learning.postman.com/docs/collections/using-newman-cli/command-line-integration-with-newman/
  - Okay if I had just click the first two tutorial links...
- https://nodejs.org/en/download/package-manager
- https://github.com/nodesource/distributions#debinstall

```console
$ curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - &&\
    sudo apt-get install -y nodejs
```

- Install Newman (the postman from Seinfeld - https://en.wikipedia.org/wiki/Newman_(Seinfeld) :)

```console
$ npm install -g newman
```

- https://www.oauth.com/oauth2-servers/client-registration/client-id-secret/
- https://github.com/w3c-ccg/traceability-interop/tree/main/docs/tutorials/authentication#example-run-postman-collection-from-the-command-line
  - MOTHERFUCKER IT WAS RIGHT THERE AT THE BOTTOM OF THE TUTORIAL AAAAAAAAAAAAAAAHHHHHHHHHHHHHHHHHHHH
    - This is what happens when one does not read and just skims... was `return -ETOOSTRESSEDOUT` at the time.

```console
$ npx newman run ./authentication.postman_collection.json \
    --env-var CLIENT_ID=$CLIENT_ID \
    --env-var CLIENT_SECRET=$CLIENT_SECRET \
    --env-var TOKEN_AUDIENCE=$TOKEN_AUDIENCE \
    --env-var TOKEN_ENDPOINT=$TOKEN_ENDPOINT \
    --reporters cli,json
```

- https://www.rfc-editor.org/rfc/rfc6749.html
- https://github.com/w3c-ccg/traceability-interop/blob/7bef64ae78ead17aa4c9baaee6061da7612b6e1d/docs/tutorials/workflow-join/README.md
  - This is similar to our ActivityPub setup
- https://github.com/w3c-ccg/traceability-interop/pull/491
  - Checking up on where their state of art is
- https://github.com/OpenAPITools/openapi-generator
  - We'll just try to generate a server to start and then explore KERI interop and the bridge from ActivityPub methodology from [RFCv4: IETF SCITT: Use Case: OpenSSF Metrics: activitypub extensions for security.txt](https://github.com/ietf-scitt/use-cases/blob/8ab06ebf523c4cef766bddac2931eaba721d9ecd/openssf_metrics.md#openssf-metrics)
  - If things go well we'll register via `Test Suite Registration`
    - https://github.com/w3c-ccg/traceability-interop/blob/main/environment-setup/README.md
- We might need OAuth2 values, we may want to leverage DEX, we'll see
  - https://github.com/dexidp/dex

```console
$ git clone https://github.com/w3c-ccg/traceability-interop.git
$ cd traceability-interop
$ npm i
$ npm run serve
^C
```

- Seems like that just serves the repo contents
  - This is like a maze of things that we try to avoid, GUIs, conda...
    - #977
- Followed the [Getting Started](https://github.com/w3c-ccg/traceability-interop/tree/main/reporting) link to the reporting directory

```console
$ cd reporting
$ python -m venv .venv
$ . .venv/bin/activate
$ pip install -r requirements.txt
```

- Run the reporting

```console
$ ./reporter.py --conformance
Processing identified reports: 4
GS1US: Conformance Suite:   0%|                                                                                                                                                            | 0/4 [00:00<?, ?it/s]No assertions found in execution Clear Token Cache
No assertions found in execution Clear DID Web Cache
Mavennet: Conformance Suite:  25%|████████████████████████████████████▎                                                                                                            | 1/4 [00:01<00:01,  1.57it/s]No assertions found in execution Clear Token Cache
No assertions found in execution Clear DID Web Cache
mesur.io: Conformance Suite:  50%|████████████████████████████████████████████████████████████████████████▌                                                                        | 2/4 [00:01<00:01,  1.56it/s]No assertions found in execution Clear Token Cache
No assertions found in execution Clear DID Web Cache
Transmute: Conformance Suite:  75%|████████████████████████████████████████████████████████████████████████████████████████████████████████████                                    | 3/4 [00:02<00:00,  1.54it/s]No assertions found in execution Clear Token Cache
No assertions found in execution Clear DID Web Cache
Transmute: Conformance Suite: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 4/4 [00:02<00:00,  1.54it/s]
Persisting raw fetched data
Processing data
Saving data frames
Saving: df_crosstab_results_multi: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 11/11 [00:00<00:00, 1783.29it/s]
100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 11/11 [00:00<00:00, 4779.09it/s]
100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 11/11 [00:00<00:00, 4402.42it/s]
<dash.dash.Dash object at 0x7f3ec84be2e0>
Dash is running on http://127.0.0.1:8050/

 * Serving Flask app 'reporter'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:8050
Press CTRL+C to quit
127.0.0.1 - - [24/Mar/2023 06:16:09] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [24/Mar/2023 06:16:09] "GET /_dash-component-suites/dash/deps/polyfill@7.v2_3_1m1679663645.12.1.min.js HTTP/1.1" 200 -
127.0.0.1 - - [24/Mar/2023 06:16:09] "GET /_dash-component-suites/dash/dash-renderer/build/dash_renderer.v2_3_1m1679663645.min.js HTTP/1.1" 200 -
127.0.0.1 - - [24/Mar/2023 06:16:09] "GET /_dash-component-suites/dash_bootstrap_components/_components/dash_bootstrap_components.v1_4_1m1679663648.min.js HTTP/1.1" 200 -
127.0.0.1 - - [24/Mar/2023 06:16:09] "GET /_dash-component-suites/dash/deps/prop-types@15.v2_3_1m1679663645.7.2.min.js HTTP/1.1" 200 -
127.0.0.1 - - [24/Mar/2023 06:16:09] "GET /_dash-component-suites/dash/deps/react@16.v2_3_1m1679663645.14.0.min.js HTTP/1.1" 200 -
127.0.0.1 - - [24/Mar/2023 06:16:09] "GET /_dash-component-suites/dash/deps/react-dom@16.v2_3_1m1679663645.14.0.min.js HTTP/1.1" 200 -
127.0.0.1 - - [24/Mar/2023 06:16:09] "GET /_dash-component-suites/dash/dcc/dash_core_components.v2_3_0m1679663645.js HTTP/1.1" 200 -
127.0.0.1 - - [24/Mar/2023 06:16:09] "GET /_dash-component-suites/dash/dcc/dash_core_components-shared.v2_3_0m1679663645.js HTTP/1.1" 200 -
127.0.0.1 - - [24/Mar/2023 06:16:09] "GET /_dash-component-suites/dash/dash_table/bundle.v5_1_1m1679663645.js HTTP/1.1" 200 -
127.0.0.1 - - [24/Mar/2023 06:16:09] "GET /_dash-component-suites/dash/html/dash_html_components.v2_0_2m1679663645.min.js HTTP/1.1" 200 -
127.0.0.1 - - [24/Mar/2023 06:16:10] "GET /_dash-layout HTTP/1.1" 200 -
127.0.0.1 - - [24/Mar/2023 06:16:10] "GET /_dash-dependencies HTTP/1.1" 200 -
127.0.0.1 - - [24/Mar/2023 06:16:10] "GET /_dash-component-suites/dash/dash_table/async-highlight.js HTTP/1.1" 200 -
127.0.0.1 - - [24/Mar/2023 06:16:10] "GET /_dash-component-suites/dash/dash_table/async-table.js HTTP/1.1" 200 -
127.0.0.1 - - [24/Mar/2023 06:16:10] "GET /_dash-component-suites/dash/dcc/async-graph.js HTTP/1.1" 200 -
127.0.0.1 - - [24/Mar/2023 06:16:10] "GET /_dash-component-suites/dash/dcc/async-plotlyjs.js HTTP/1.1" 200 -
127.0.0.1 - - [24/Mar/2023 06:16:16] "GET /_favicon.ico?v=2.3.1 HTTP/1.1" 200 -
```

- The whole thing is javascript, lynx won't dump it
  - https://fathy.fr/carbonyl
    - This renders chrome to a terminal, we'll want to play with it eventually

![image](https://user-images.githubusercontent.com/5950433/227532248-48808340-8dfb-42a4-9160-d16746326715.png)

- Check the CI jobs
  - https://github.com/w3c-ccg/traceability-interop/blob/main/.github/workflows/regression-workflow-instance-join.yml
  - Finally, sanity
  - https://github.com/w3c-ccg/traceability-interop/blob/7bef64ae78ead17aa4c9baaee6061da7612b6e1d/.github/workflows/interoperability-report.yml
- https://w3c-ccg.github.io/traceability-interop/openapi/#tag--Identifiers
- https://dexidp.io/docs/connectors/oauth/
  - Okay DEX helps us bridge OAuth to OIDC, I forgot, it's been a while
- https://github.com/OpenAPITools/openapi-generator/blob/master/docs/online.md
  - Let's try to generate a server side API
  - https://github.com/OpenAPITools/openapi-generator#to-generate-a-sample-client-library
- Wow fucking java this really is the perfectly designed maze

```console
$ sudo apt install -y default-jre maven
$ git clone --depth=1 https://github.com/OpenAPITools/openapi-generator
$ cd openapi-generator
$ ./bin/generate-samples.sh ./bin/configs/java-okhttp-gson.yaml
```

- Successful generation of example
- https://github.com/OpenAPITools/openapi-generator/tree/master/samples/server/petstore/python-aiohttp
- Now to generate server, our `dffml-service-http` already uses aiohttp
- https://github.com/spec-first/connexion
  - > Swagger/OpenAPI First framework for Python on top of Flask with automatic endpoint validation & OAuth2 support
  - Fuck ya we're back in happy land
- Now to generate an aiohttp server based off the traceability-interop spec
  - https://github.com/w3c-ccg/traceability-interop/blob/main/tests/traceability-v1.jsonld
  - https://github.com/w3c-ccg/traceability-interop/blob/main/tests/valid-credential.json
  - https://github.com/w3c-ccg/traceability-interop/blob/main/docs/openapi/openapi.yml

```console
$ java -ea -server -Duser.timezone=UTC \
    -jar modules/openapi-generator-cli/target/openapi-generator-cli.jar generate \
    -g python-aiohttp \
    -i ../traceability-interop/docs/openapi/openapi.yml \
    -o python-aiohttp-traceability-interop
[main] INFO  o.o.codegen.utils.ModelUtils - [deprecated] inheritance without use of 'discriminator.propertyName' has been deprecated in the 5.x release. Composed schema name: null. Title: null
[main] INFO  o.o.codegen.utils.ModelUtils - [deprecated] inheritance without use of 'discriminator.propertyName' has been deprecated in the 5.x release. Composed schema name: null. Title: null
[main] INFO  o.o.codegen.utils.ModelUtils - [deprecated] inheritance without use of 'discriminator.propertyName' has been deprecated in the 5.x release. Composed schema name: null. Title: Revocation List Verifiable Credential
[main] INFO  o.o.codegen.utils.ModelUtils - [deprecated] inheritance without use of 'discriminator.propertyName' has been deprecated in the 5.x release. Composed schema name: null. Title: Verifiable Presentation
[main] INFO  o.o.codegen.utils.ModelUtils - [deprecated] inheritance without use of 'discriminator.propertyName' has been deprecated in the 5.x release. Composed schema name: null. Title: Verifiable Credential
[main] INFO  o.o.codegen.utils.ModelUtils - [deprecated] inheritance without use of 'discriminator.propertyName' has been deprecated in the 5.x release. Composed schema name: null. Title: Credential Linked Data Proof
[main] INFO  o.o.codegen.utils.ModelUtils - [deprecated] inheritance without use of 'discriminator.propertyName' has been deprecated in the 5.x release. Composed schema name: null. Title: Traceable Presentation
[main] INFO  o.o.codegen.utils.ModelUtils - [deprecated] inheritance without use of 'discriminator.propertyName' has been deprecated in the 5.x release. Composed schema name: null. Title: Presentation Linked Data Proof
Exception in thread "main" org.openapitools.codegen.SpecValidationException: There were issues with the specification. The option can be disabled via validateSpec (Maven/Gradle) or --skip-validate-spec (CLI).
 | Error count: 5, Warning count: 0
Errors:
        -attribute components.responses.$ref is not of type `object`
        -attribute components.schemas.$ref is not of type `object`
        -components.schemas.Schema name $ref doesn't adhere to regular expression ^[a-zA-Z0-9\.\-_]+$
        -components.parameters.Parameter name $ref doesn't adhere to regular expression ^[a-zA-Z0-9\.\-_]+$
        -components.responses.Response key $ref doesn't adhere to regular expression ^[a-zA-Z0-9\.\-_]+$

        at org.openapitools.codegen.config.CodegenConfigurator.toContext(CodegenConfigurator.java:620)
        at org.openapitools.codegen.config.CodegenConfigurator.toClientOptInput(CodegenConfigurator.java:647)
        at org.openapitools.codegen.cmd.Generate.execute(Generate.java:479)
        at org.openapitools.codegen.cmd.OpenApiGeneratorCommand.run(OpenApiGeneratorCommand.java:32)
        at org.openapitools.codegen.OpenAPIGenerator.main(OpenAPIGenerator.java:66)
```

- The generator is unhappy with the input file from traceability-interop

**traceability-interop.git/docs/openapi/openapi.yml**

```yaml
openapi: '3.0.0'
info:
  version: 1.0.0
  title: Open API for Interoperable Traceability
  description: Identifier and Credentials APIs for DID.
  license:
    name: Apache 2.0
    url: https://www.apache.org/licenses/LICENSE-2.0.html

servers:
  - url: https://api.did.actor

tags:
  - name: Discovery
  - name: Identifiers
  - name: Credentials
  - name: Presentations

paths:
  /did.json:
    $ref: './resources/api-configuration.yml'

  /identifiers/{did}:
    $ref: './resources/did.yml'

  /credentials/issue:
    $ref: './resources/credential-issuer.yml'
  /credentials/status:
    $ref: './resources/credential-status.yml'
  /credentials/verify:
    $ref: './resources/credential-verifier.yml'
  /credentials/{credential-id}:
    $ref: './resources/credential.yml'

  /presentations:
    $ref: './resources/presentations.yml'
  /presentations/prove:
    $ref: './resources/presentation-prover.yml'
  /presentations/verify:
    $ref: './resources/presentation-verifier.yml'
  /presentations/available:
    $ref: './resources/presentation-available.yml'
  /presentations/submissions:
    $ref: './resources/presentation-submissions.yml'

components:
  securitySchemes:
    OAuth2:
      type: oauth2
      flows:
        clientCredentials:
          tokenUrl: https://example.com/oauth/token
          scopes:
            'resolve:dids': Grants permission to resolve DIDs
            'issue:credentials': Grants permission issue Verifiable Credentials
            'verify:credentials': Grants permission verify Verifiable Credentials
            'read:credentials': Grants permission to get Verifiable Credentials
            'update:credentials': Grants permission to update the status of Verifiable Credentials
            'prove:presentations': Grants permission to prove Verifiable Presentations
            'verify:presentations': Grants permission verify Verifiable Presentations
            'submit:presentations': Grants permission to submit Verifiable Presentations
  parameters:
    $ref: './parameters/_index.yml'
  schemas:
    $ref: './schemas/_index.yml'
  responses:
    $ref: './responses/_index.yml'
```

- It looks like those `$ref` tags need to be resolved to their file locations
  - Does the `reporter.py` already have code to do this?

```console
$ pip install pyyaml
$ python -c 'import yaml, sys, pathlib; target = pathlib.Path(sys.argv[-1]).resolve(); root = yaml.safe_load(target.read_text()); print(root)' ../traceability-interop/docs/openapi/openapi.yml
```

- This will be a multi-line thing, there are many `$ref`s to load
  - https://gist.github.com/pdxjohnny/ee54079831991d9155b457adb634b78b

```console
$ (cd ~/.local/ && npm install nodemon)
$ . <(echo 'export PATH="${PATH}:${HOME}/.local/node_modules/.bin"')
$ echo 'export PATH="${PATH}:${HOME}/.local/node_modules/.bin"' | tee -a ~/.bashrc
$ . ~/.bashrc
```

- Ah, upon closer inspection, found the dereference command

```
package.json:    "preserve": "npx swagger-cli bundle docs/openapi/openapi.yml -o docs/openapi/openapi.json --dereference",
```

- Run it from the root of the traceability-interop repo

```console
$ npx swagger-cli bundle docs/openapi/openapi.yml -o docs/openapi/openapi.json --dereference
Created docs/openapi/openapi.json from docs/openapi/openapi.yml
```

- Success!
  - https://gist.github.com/435c76fb52b7399a2debea6643252179
- Now to install the package for the server we just generated and run the tests
  - Then we'll see how OAuth is configured
  - Then we'll try to add this new service stub as a test
    - Then we'll play with DWN as a backend from the stub

```console
$ cd python-aiohttp-traceability-interop/
$ python -m pip install -r requirements.txt -r test-requirements.txt -e .
$ pytest
```

- Failures abound!
  - It looks like they are all related to some YAML bug loading timestamps?
- Tried gen to fastapi but pydantic properties with `-` in them were generated
  - https://github.com/OpenAPITools/openapi-generator/issues/11610
- https://gist.github.com/enten/c4f9e35279c1278844c3
  - This looks nice for our 2nd party auto split out
- https://github.com/ossf/wg-vulnerability-disclosures/issues/94#issuecomment-1483184591
  - Not sure if this is still active, but have been working on a methodology as part of this SCITT use case: [WIP: RFCv4: IETF SCITT: Use Case: OpenSSF Metrics: activitypub extensions for security.txt](https://github.com/ietf-scitt/use-cases/blob/748597b37401bd59512bfedc80158b109eadda9b/openssf_metrics.md#openssf-metrics). In this use case we're looking at OpenVEX as the format which we could use to submit the vuln. We'd use the description or evolution of the linked data format there to reference a SARIF or other standard format document or set of instances of formats which would act as the justification, with the status set to affected. Effectively proposing that this ad-hoc generated CVE-ID affects the product. Perhaps a schema for the example form above is needed / could be part of the vocabulary involved?
    - [https://github.com/intel/dffml/blob/alice/schema/security/vuln/proposed/0.0.0.schema.json](https://github.com/intel/dffml/blob/9303cbee00690d3b7ba3fb673d5402a3965cfdc0/schema/security/vuln/proposed/0.0.0.schema.json)

```yaml
$id: https://github.com/intel/dffml/raw/main/schema/security/vuln/proposed/0.0.0.schema.json
$schema: https://json-schema.org/draft/2020-12/schema
definitions:
  affected_version:
    description: What Product, OS, stack and versions have you tested against? TODO
      regex for PURLs
    type: string
  entity:
    description: Who done it
    properties:
      name:
        description: Whooooo areeeeee youuuuuu?
        type: string
    type: object
  exploitation_technique:
    description: How can did you break it?
    enum:
    - local
    - remote
    type: string
  mitigation:
    description: Any suggestions on how to fix it?
    type: string
  poc:
    description: POC Code and/or steps to reproduce (can attach a file, base64 encode
      a zip or tar for now if a repo or more than one file)
    type: string
  proposed_vuln:
    properties:
      affected_versions:
        items:
          $ref: '#/definitions/affected_version'
        type: array
      credits:
        items:
          $ref: '#/definitions/entity'
        type: array
      description:
        description: "Short, yet descriptive overview of what you\u2019ve found"
        type: string
      exploitation_techniques:
        items:
          $ref: '#/definitions/exploitation_technique'
        type: array
      mitigation:
        $ref: '#/definitions/mitigation'
      poc:
        $ref: '#/definitions/poc'
      timeline:
        $ref: '#/definitions/timeline'
    type: object
  timeline:
    description: What are we thinking the order of events related to responsible discloure
      is?
    items:
      $ref: '#/definitions/timeline_item'
    type: array
  timeline_item:
    description: Something is happneing!
    properties:
      date:
        description: When is this timeline itme happening. TODO date regex. TODO non-linear
          time conversion helpers
        type: string
      description:
        description: What's happening at this point in time?
        type: string
      parties:
        description: Who's involved in this timeline item?
        items:
          $ref: '#/definitions/entity'
        type: array
    type: object
properties:
  '@context':
    items:
      type: string
    type: array
  include:
    items:
      $ref: '#/definitions/proposed_vuln'
    type: array
```

```console
$ python -m pip install python-jwt pyyaml
$ python -c 'import sys, python_jwt, yaml; print(yaml.dump(list(python_jwt.process_jwt(sys.argv[-1]))))'
```

- https://chromium.googlesource.com/chromium/src/+/main/docs/contributing.md#running-automated-tests
  - Ref yestredays codeql on workflows, auto ploicy based approval or workload execution for 2nd party
    - 3rd party would be strickter policy for promotion
    - 2nd party involves same oras.land as first party
      - Since they are support level 1
- Checking for what kinds of BOMs exist within traceability-vocab currently

```console
$ curl -sfL https://github.com/w3c-ccg/traceability-vocab/raw/5221dec607706deabfbf2b5b9179c03088ede79c/docs/credentials-with-undefined-terms.json | grep -i billof
    "type": "SoftwareBillofMaterialsCredential",
    "type": "MultiModalBillOfLadingCredential",
    "type": "MasterBillOfLadingCredential",
    "type": "HouseBillOfLadingCredential",
    "type": "BillOfLadingCredential",
```

- Looks like vulns still need to be added to traceability vocab

```console
$ curl -sfL https://github.com/w3c-ccg/traceability-vocab/raw/5221dec607706deabfbf2b5b9179c03088ede79c/docs/credentials-with-undefined-terms.json | grep -i vuln
```

- https://github.com/w3c-ccg/traceability-vocab/issues/596
  - Here's a possible way for us to bridge from ActivityPub status IDs
- https://rdflib.readthedocs.io/en/stable/security_considerations.html#python-runtime-audit-hooks

```console
$ cd schema/security/vuln/proposed/
$ python -c "import sys, pathlib, json, yaml; pathlib.Path(sys.argv[-1]).write_text(json.dumps(yaml.safe_load(pathlib.Path(sys.argv[-2]).read_text()), indent=4) + '\n')" example.0.0.0.yaml example.0.0.0.json
$ jsonschema --instance example.0.0.0.json 0.0.0.schema.json
$ echo $?
0
```

- TODO
  - [x] Find example cvemap code for Arif
    - [ ] Send email to mailing list
      - Mention it works with https://github.com/intel/cve-bin-tool/blob/main/cve_bin_tool/cvedb.py
        - https://github.com/intel/cve-bin-tool/pull/277
        - https://github.com/intel/cve-bin-tool/pull/285
  - [x] Tell Katherine today's the day we're playing with traceability interop
  - [ ] Add proposed vuln to https://github.com/w3c-ccg/traceability-vocab
  - [ ] Update Manifest ADR to reference check-jsonschema
    - https://github.com/python-jsonschema/check-jsonschema
  - [ ] `await reponse_from("Ariadne")`