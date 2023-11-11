A GitHub Public Key and TPM Based Supply Chain Security Mitigation Option
#########################################################################

Example of dependency hot swap https://github.com/alice/httptest/

The DID: ``did:github-release-body-parse-number-35:alice:httptest:0.1.5``

Lookup ``alice`` witin https://github.com/alice.keys

.. code-block::

    ssh-rsa AAA...AAA httptest/httptest-0.1.4-signer/httptest-0.1.5-signer
    ssh-rsa AAA...AAA httptest-0.1.4-signer
    ssh-rsa AAA...AAA httptest-0.1.5-signer

search each key comment for one that starts with ``httptest/`` behind the slash
split on ``/`` to find the keys which signed each release.

With Federated forges (long term target in WASM environment) we can leverage
this ssh method ideally with an attested Transparency Service
then we can get a receipt, issused with an ssh ECDSA-384 key.

CWT issuer is the keys endpoint.

We can use https://github.com/tpm2-software/tpm2-pkcs11 to bind the keys to a
TPM owned by the developer.

TODO

- Investigate binding keys to a FIDO style key (things like YubiKeys)
