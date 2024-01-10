## 2024-01-08 SCITT

- Triaging issues on arch doc
- Dep diagram from Orie
  - https://github.com/ietf-wg-scitt/draft-ietf-scitt-architecture/issues/148

```mermaid
flowchart 
    
subgraph COSE
    cometre[draft-ietf-cose-merkle-tree-proofs]
    hash-envelope{{draft-steele-cose-hash-envelope}}
end

subgraph SCITT
    architecture[draft-ietf-scitt-architecture]
    scrapi{{draft-birkholz-scitt-scrapi}}
    cometre-ccf{{draft-birkholz-cose-cometre-ccf-profile}}
end

scrapi --> architecture
architecture -->  cometre
architecture --> hash-envelope
cometre-ccf --> cometre
```

- https://github.com/ietf-wg-scitt/draft-ietf-scitt-architecture/issues/79
- https://github.com/ietf-wg-scitt/draft-ietf-scitt-architecture/issues/120
  - Verifier checks crypto
  - Relying party needs crypto checked, and as vested intrest in payload
- https://github.com/ietf-wg-scitt/draft-ietf-scitt-architecture/issues/151
  - Same stuff Cedric introduced at 118
- https://github.com/ietf-wg-scitt/draft-ietf-scitt-architecture/pulls/142
  - Connections to Key Transparency need to be included