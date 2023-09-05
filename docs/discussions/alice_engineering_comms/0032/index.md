# 2022-09-20 Engineering Log

- https://github.com/TheAliceProject
  - > The Alice Project at Carnegie Mellon University's Entertainment Technology Center is dedicated to creating tools to teach computer science through creativity. http://alice.org/
- https://fluxcd.io/blog/2022/08/manage-kyverno-policies-as-ocirepositories/
  - Admission control k8s policy controller with kyverno storing policies as artifacts in oci reg
    - Could we have sbom stored as povenace for policy?
    - Sbom for policy includes data sets and docs and org contacts
- The cells are working together
  - ad-hoc over time (within lifetime tick and tock, mutation/fork/downstream/patched/evolution) distributed by function
  - Communication through both peer to peer and central stream of consiousness
- analogy using LTMs and OpenSSF scorecard and LEED certification
  - https://support.usgbc.org/hc/en-us/articles/4404406912403-What-is-LEED-certification-#LEED
  - Analogy point is focus on time (beyond the onion security model, defense in depth pver tome requires maintainance)
- time for kcp stream!
  - https://twitter.com/lorenc_dan/status/1572181327788777476?s=20&t=dvaRWcxul3i94V8vqYMG9A
  - Kcp spec as manifest reverse proxy to jenkins
  - KCP on top of OpenFaaS managed by ArgoCD
    - Alice creates PRs to state config
    - SBOMS: https://github.com/opensbom-generator/spdx-sbom-generator/blob/main/examples/modules.json
  - DERP (see https://goto.intel.com/devenvdocs deployment engineering logs)
We can use this as the stream proxy (everything speaks HTTP)

![TrinityCalls](https://user-images.githubusercontent.com/5950433/191273573-c5a805d5-48e9-49cc-aa84-680ded4b401f.gif)

- Lock established
  - Model mixes via Overlays and DataFlow as class
    - stable diffusion examples
- Rewarding alignment doc deck
  - https://www.sphinx-doc.org/en/master/usage/builders/index.html#sphinx.builders.latex.LaTeXBuilder
- Use case doc
- Need faster way to edit github discussion as markdown
  - Could we do `python -m rich.markdown FILENAME` on one side and a reupload on the other?
    - Problem: drag and drop pictures
  - https://rich.readthedocs.io/en/stable/markdown.html
- https://github.com/guacsec/guac
  - Similar to SCITT
    - Will collaberate with them
    - OA is essentially adding policy to assit with managing lifecycle (patching vulns and retesting downstreams and rereleasing defined in Part / checjed via policy)
- TODO
  - [ ] Type up context aware policy notes