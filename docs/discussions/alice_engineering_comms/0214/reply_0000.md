## 2023-03-21 @pdxjohnny Engineering Logs

- https://github.com/seferov/pr-lint-action
- https://github.com/GerevAI/gerev
- https://pypi.org/help/#project-release-notifications
  - Can we work with them to do release notifications via ActivityPub? Should we ping Aria?
  - We can of course setup rss rebroadcast
    - We need the eventing (`/inbox`) because of the AI, it helps us facilitate the abstract compute architecture event loop
      - `Rolling Alice: (Preface:) Transport Acquisition: Abstract Compute Architecture`
- https://github.com/in-toto/attestation/pull/164
- https://github.com/in-toto/attestation/pull/162
- https://github.com/in-toto/attestation/pull/152
- https://github.com/in-toto/attestation/pull/151
- https://github.com/in-toto/attestation/pull/129
- https://github.com/w3c/vc-data-model/issues/1063
- https://sourceware.org/git/?p=glibc.git;a=blob_plain;f=sysdeps/unix/sysv/linux/x86_64/clone.S;hb=HEAD
- TODO
  - [ ] Plan tutorial where we injest the shared stream of consiousness and feed it into performant analysis to help Alice do online learning on the open source software lifecycle
    - https://paimon.apache.org/docs/master/engines/spark3/
    - https://paimon.apache.org/docs/master/concepts/append-only-table/
      - Patch for transparency service insert?
  - [ ] Document alignment with https://github.com/in-toto/attestation/blob/main/spec/predicates/link.md
    - [ ] Contribute some alignment with Verifiable Credentials to bridge to the verified JSON-LD landscape
      - Ideally we align to KERIVC
        - This would be chadig.com
  - [ ] https://github.com/in-toto/attestation/pull/162
  - [ ] https://github.com/in-toto/attestation/issues/165#issuecomment-1478420542
    - Resource descriptor would be good to look at
      - Download locations, URIs - Could we just throw a VC URI there? Similar to ActivityPub exetensions for security.txt/md where we just say, there's a Contact-URL, just set it to an activitypub actor
      - Would all that verification code from those DIF WGs transfer?

![much-acc](https://user-images.githubusercontent.com/5950433/226707682-cfa8dbff-0908-4a34-8540-de729c62512f.png)