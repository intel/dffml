- Drop all the primitive stuff, a definition, is a system context, is an input (DID)

Minimal trusted deployment:


Example of dependency hot swap https://github.com/pdxjohnny/httptest/

The DID: `did:github-release-body-parse-number-35:pdxjohnny:httptest:0.1.5`

Lookup `pdxjohnny` witin https://github.com/pdxjohnny.keys

```
ssh-rsa AAA...AAA httptest/httptest-0.1.4-signer/httptest-0.1.5-signer
ssh-rsa AAA...AAA httptest-0.1.4-signer
ssh-rsa AAA...AAA httptest-0.1.5-signer
```

search each key comment for one that starts with `httptest/` behind the slash
split on `/` to find the keys which signed each release.


