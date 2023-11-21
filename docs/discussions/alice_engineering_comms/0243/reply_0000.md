## 2023-04-19 @pdxjohnny Engineering Logs

- https://github.com/wolfi-dev/os/commit/40c24089d4a16c594d3e30c4c232e14fa18ce6e2
  - nats for guac
- node 20 enables the binary packaging we wanted for activitypub starter kit

![chaos-for-the-chaos-god](https://user-images.githubusercontent.com/5950433/220794351-4611804a-ac72-47aa-8954-cdb3c10d6a5b.jpg)

- https://authzed.com/blog/pitfalls-of-jwt-authorization
  - something something in memory db

```console
$ docker build --progress plain -t $(basename $(dirname .github/actions/create_manifest_instance_build_images_containers/Dockerfile | sed -e 's/\.Dockerfile//g' -e 's/_/-/g')) -f .github/actions/create_manifest_instance_build_images_containers/Dockerfile .github/actions/create_manifest_instance_build_images_containers/
```

- https://rdflib.readthedocs.io/en/stable/_modules/examples/secure_with_urlopen.html#

```python
"""
License: BSD 3-Clause

This example demonstrates how to use a custom global URL opener installed with `urllib.request.install_opener` to block access to URLs.

- References
  - https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.plugins.parsers.html#module-rdflib.plugins.parsers.jsonld

from rdflib import Graph, URIRef, Literal
test_json = '''
{
    "@context": {
        "dc": "http://purl.org/dc/terms/",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
    },
    "@id": "http://example.org/about",
    "dc:title": {
        "@language": "en",
        "@value": "Someone's Homepage"
    }
}
'''
g = Graph().parse(data=test_json, format='json-ld')
list(g) == [(URIRef('http://example.org/about'),
    URIRef('http://purl.org/dc/terms/title'),
    Literal("Someone's Homepage", lang='en'))]

  - https://rdflib.readthedocs.io/en/stable/_modules/examples/secure_with_urlopen.html
    - Upstream
"""
import http.client
import logging
import os
import sys
from typing import Optional
from urllib.request import HTTPHandler, OpenerDirector, Request, install_opener

from rdflib import Graph


class SecuredHTTPHandler(HTTPHandler):
    def http_open(self, req: Request) -> http.client.HTTPResponse:
        # TODO Protect with SCITT
        # - https://scitt.io/distributing-with-oci-scitt.html
        # TODO Query the registry
        # - https://oras.land/
        #   - https://github.com/oras-project/oras-credentials-go
        # - https://github.com/oras-project/oras-py
        #   - https://oras-project.github.io/oras-py/
        #     - https://docs.python.org/3/library/unittest.mock.html#patch-object
        if req.get_full_url().endswith("blocked.jsonld"):
            raise PermissionError("Permission denied for URL")
        return super().http_open(req)



def main() -> None:
    logging.basicConfig(
        level=os.environ.get("PYTHON_LOGGING_LEVEL", logging.INFO),
        stream=sys.stderr,
        datefmt="%Y-%m-%dT%H:%M:%S",
        format=(
            "%(asctime)s.%(msecs)03d %(process)d %(thread)d %(levelno)03d:%(levelname)-8s "
            "%(name)-12s %(module)s:%(lineno)s:%(funcName)s %(message)s"
        ),
    )

    opener = OpenerDirector()
    opener.add_handler(SecuredHTTPHandler())
    install_opener(opener)

    graph = Graph()

    # Attempt to parse a JSON-LD document that will result in the blocked URL
    # being accessed.
    error: Optional[PermissionError] = None
    try:
        graph.parse(
            data=r"""{
            "@context": "http://example.org/blocked.jsonld",
            "@id": "example:subject",
            "example:predicate": { "@id": "example:object" }
        }""",
            format="json-ld",
        )
    except PermissionError as caught:
        logging.info("Permission denied: %s", caught)
        error = caught

    # `Graph.parse` would have resulted in a `PermissionError` being raised from
    # the url opener.
    assert isinstance(error, PermissionError)
    assert error.args[0] == "Permission denied for URL"



if __name__ == "__main__":
    main()
```

![knowledge-graphs-for-the-knowledge-god](https://user-images.githubusercontent.com/5950433/222981558-0b50593a-c83f-4c6c-9aff-1b553403eac7.png)

- https://github.com/ossf/wg-vulnerability-disclosures/issues/74
- https://app.slack.com/client/T019QHUBYQ3/C05009RHCNT
  - TODO: Anyone playing with the json-ld-ness of openvex yet?
- https://github.com/in-toto/attestation/pull/192
  - Great proto regen example
- https://github.com/in-toto/attestation/blob/3df726cfcc0528dcbdb4d45ed1597b793d1b777d/spec/predicates/scai.md

```json
{
    // Standard attestation fields
    "_type": "https://in-toto.io/Statement/v1",
    "subject": [{
        "name": "my-app",
        "digest": { "sha256": "78ab6a8..." }
    }],
        
    "predicateType": "https://in-toto.io/attestation/scai/attribute-report/v0.2",
    "predicate": {
        "attributes": [{
            "attribute": "ATTESTED_DEPENDENCIES",
            "target": {
                "name": "my-rsa-lib.so",
                "digest": { "sha256": "ebebebe..." },
                "uri": "http://example.com/libraries/my-rsa-lib.so"
            }
            "evidence": {
                "name": "rsa-lib-attribute-report.json",
                "digest": { "sha256": "0987654..." },
                "mediaType": "application/x.dsse+json"
            }
        }],
        "producer": {
            "uri": "https://example.com/my-github-actions-runner",
        }
    }
}
```

```json
{
    // Standard attestation fields
    "_type": "https://in-toto.io/Statement/v1",
    "subject": [{
        "name": "my-sgx-builder",
        "digest": { "sha256": "78ab6a8..." }
    }],
        
    "predicateType": "https://in-toto.io/attestation/scai/attribute-report/v0.2"
    "predicate": {
        "attributes": [{
            "attribute": "HARDWARE_ENCLAVE",
            "target": {
                "name": "enclave.signed.so",
                "digest": { "sha256": "e3b0c44..." },
                "uri": "http://example.com/enclaves/enclave.signed.so",
            },
            "evidence": {
                "name": "my-sgx-builder.json",
                "digest": { "sha256": "0987654..." },
                "downloadLocation": "http://example.com/sgx-attestations/my-sgx-builder.json",
                "mediaType": "application/x.sgx.dcap1.14+json"
            }
       }]
    }
}
```

```json
{
    // Standard attestation fields
    "_type": "https://in-toto.io/Statement/v1",
    "subject": [{
        "name": "app-evidence-collection",
        "digest": { "sha256": "88888888..." }
    }],
        
    "predicateType": "https://in-toto.io/attestation/scai/attribute-report/v0.2",
    "predicate": {
        "attributes": [{
            "attribute": "attestation-1",
            "evidence": {
                "uri": "https://example.com/attestations/attestation-1"
                "digest": { "sha256": "abcdabcd..." },
                "mediaType": "application/x.dsse+json"
            }
        },
        {
            "attribute": "attestation-2",
            "evidence": {
                "uri": "https://example.com/attestations/attestation-2"
                "digest": { "sha256": "01234567..." },
                "mediaType": "application/x.dsse+json"
            }
        },
        {
            "attribute": "attestation-3",
            "evidence": {
                "uri": "https://example.com/attestations/attestation-3"
                "digest": { "sha256": "deadbeef..." },
                "mediaType": "application/x.dsse+json"
            }
        }],
        "producer": { "uri": "https://my-sw-attestor" }
    }
}
```

- https://github.com/in-toto/attestation/blob/3df726cfcc0528dcbdb4d45ed1597b793d1b777d/spec/predicates/scai.md#attestation-for-evidence-collection
  - https://github.com/guacsec/guac/commit/07674704d005549186540874c1b16d823499c1fb
    - Looks like we might leverage our SCITT receipts here
- https://github.com/in-toto/attestation/blob/e53cd3b10d4a7a8dcab5c9efd87bedd006eba270/spec/predicates/README.md
  - Existing list of predicates
    - https://github.com/in-toto/attestation/blob/e53cd3b10d4a7a8dcab5c9efd87bedd006eba270/spec/predicates/runtime-trace.md
      - https://github.com/CycloneDX/cyclonedx-python
      - https://github.com/CycloneDX/specification/pull/200
      - https://github.com/CycloneDX/specification/pull/209
      - https://github.com/CycloneDX/specification/pull/194
        - trustZone
- https://github.com/intel-ai/hdk#query-execution
- https://modin.readthedocs.io/en/stable/
- https://docs.siliconcompiler.com/en/stable/user_guide/programming_model.html
- TODO
  - [ ] Vuln disclosure form and OpenVEX in registry with JSON-LD linking to assets `FROM scratch` added with labels used to store schema manifest and to store comments from Dockerfile as README-esq in labels
    - https://github.com/ossf/wg-vulnerability-disclosures/issues/94#issuecomment-1483184591