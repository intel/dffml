A GitHub Public Bey and TPM Based Supply Chain Security Mitigation Option
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


