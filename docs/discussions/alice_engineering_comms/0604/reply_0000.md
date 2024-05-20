- https://github.com/actions/toolkit/tree/29885a805ef3e95a9862dcaa8431c30981960017/packages/attest#sigstore-instance
  - > - Sigstore Instance
    >
    >   - When generating the signed attestation there are two different Sigstore
    >     instances which can be used to issue the signing certificate. By default,
    >     workflows initiated from public repositories will use the Sigstore public-good
    >     instance and persist the attestation signature to the public [Rekor transparency
    >     log](https://docs.sigstore.dev/logging/overview/). Workflows initiated from
    >     private/internal repositories will use the GitHub-internal Sigstore instance
    >     which uses a signed timestamp issued by GitHub's timestamp authority in place of
    >     the public transparency log.
    >
    >     The default Sigstore instance selection can be overridden by passing an explicit
    >     value of either "public-good" or "github" for the `sigstore` option when calling
    >     either `attest` or `attestProvenance`.
    >
    > - Storage
    >
    >   - Attestations created by `attest`/`attestProvenance` will be uploaded to the GH
    >     attestations API and associated with the appropriate repository. Attestation
    >     storage is only supported for public repositories or repositories which belong
    >     to a GitHub Enterprise Cloud account.
    >
    >     In order to generate attestations for private, non-Enterprise repositories, the
    >     `skipWrite` option should be set to `true`.
- https://pr-agent-docs.codium.ai/installation/locally/#using-pip-package
- https://github.com/langfuse/langfuse-docs/blob/ed596e055a6d9baf003e8a3ba4db30ee55cc1859/cookbook/prompt_management_langchain.ipynb