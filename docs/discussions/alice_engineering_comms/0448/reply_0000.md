## 2023-11-11 @pdxjohnny Engineering Logs

- Updated ADR 7: [A GitHub Public Key and TPM Based Supply Chain Security Mitigation Option](https://github.com/intel/dffml/blob/alice/docs/arch/0007-A-GitHub-Public-Bey-and-TPM-Based-Supply-Chain-Security-Mitigation-Option.rst#a-github-public-key-and-tpm-based-supply-chain-security-mitigation-option)
  - With Federated forges (long term target in WASM environment) we can leverage this ssh method ideally with an attested Transparency Service then we can get a receipt, issused with an ssh ECDSA-384 key.
  - CWT issuer is the keys endpoint.
  - We can use https://github.com/tpm2-software/tpm2-pkcs11 to bind the keys to a TPM owned by the developer.

```bash
ssh-keygen -q -f ~/.ssh/ecdsa_384 -t ecdsa -b 384 -N '' <<<y
cat ~/.ssh/ecdsa_384 | python -c 'import sys; from cryptography.hazmat.primitives import serialization; print(serialization.load_ssh_private_key(sys.stdin.buffer.read(), password=None).private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption()).decode().rstrip())' | scitt-emulator client create-claim --issuer did:web:example.com --content-type application/json --payload '{"sun": "yellow"}' --out claim.cose --subject "ssh-test" --private-key-pem /dev/stdin
ssh-keygen -q -f /dev/stdout -t ecdsa -b 384 -N '' <<<y | python -c 'import sys; from cryptography.hazmat.primitives import serialization; print(serialization.load_ssh_private_key(sys.stdin.buffer.read(), password=None).private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption()).decode().rstrip())' | scitt-emulator client create-claim --issuer did:web:example.com --content-type application/json --payload '{"sun": "yellow"}' --out claim.cose --subject "ssh-test" --private-key-pem /dev/stdin
```

- GitHub only exports SSH keys with Key type as "Authentication Key" at https://github.com/pdxjohnny.keys

![image](https://github.com/intel/dffml/assets/5950433/5c185259-d269-4346-b111-e19982e4c1d4)

- TODO
  - [ ] Investigate binding keys to a FIDO style key (things like YubiKeys)
  - [ ] Do we have the opportunity to reduce dependence at large on OAuth fulcio style flows? Pretty sure you don't even need fulcio if you have your ssh key