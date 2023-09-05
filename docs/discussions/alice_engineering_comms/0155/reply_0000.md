## 2023-01-22 @pdxjohnny Engineering Logs

![0C075558-8EE9-44DE-B94F-8F526FFB524D](https://user-images.githubusercontent.com/5950433/213922696-75166d8f-1f97-4f6f-8913-e5ea8629f374.jpeg)

> 365 Tao - Deng Ming-Dao - 22 - Communication
>
> > Movement, objects, speech, and words:
> > We communicate through gross symbols.
> > We call them "
"objective,"
> > But we cannot escape our point of view.
>
> We cannot [currently] communicate directly from mind to mind, and so misinterpretation is a perennial problem. Motions, signs, talk-ing, and the written word are all encumbered by miscommu-nication. A dozen eyewitnesses to the same event cannot agree on a single account. We may each see something different in cards set up by a circus magician. Therefore, we are forever imprisoned by our subjectivity.
Followers of Tao assert that we know no absolute truth in the world, only varying degrees of ambiguity. Some call this poetry; some call this art. The fact remains that all communication is relative. Those who follow Tao are practical. They know that words are imperfect and therefore give them limited importance: The symbol is not the same as the reality.

- https://github.com/google-research/tuning_playbook/blob/main/README.md
- https://github.com/charmbracelet/vhs
  - Generate GIFs in CI/CD
- https://github.com/NVIDIA/container-canary
- https://github.com/containers/shortnames
  - Attempt to alias all for dev test builds of localhost.run style domains
  - https://github.com/charmbracelet/soft-serve
- https://zellij.dev/documentation/creating-a-layout.html
- https://atproto.com/guides/faq#what-is-xrpc-and-why-not-use-___
- https://github.com/charmbracelet/wishlist
- https://github.com/aurae-runtime/aurae
  - > Aurae extends [SPIFFE](https://github.com/spiffe)/[SPIRE](https://github.com/spiffe/spire) (x509 mTLS)-backed identity, authentication (authn), and authorization (authz) in a distributed system down to the Unix domain socket layer.
  - We played with this a few months back but should finish everything (2nd party, OSS scans, etc.) as container builds with scratch and ARG removal where needed first before we go back to messing with OSDecentAlice
- https://github.com/G4lile0/Heimdall-WiFi-Radar
- https://github.com/sigstore/fulcio/pull/945
  - https://github.com/sigstore/fulcio/issues/955
    - Reproduced below (we care about this see #1247, shes arriving when scitt log of scan flow)
    > I'm raising this as a potential enhancement/addition to current set of X.509 extensions used by Sigstore when encapsulating GitHub Actions OIDC claims, based on [this comment](https://internals.rust-lang.org/t/pre-rfc-using-sigstore-for-signing-and-verifying-crates/18115/14?u=woodruffw) in the pre-RFC discussion for Sigstore's integration into `cargo`/`crates.io`.
> 
> At the moment, there are two primary OIDC claims from GitHub Actions-issued tokens that get embedded in Fulcio-issued certificates as X.509v3 extensions:
> 
> 1. The SAN itself, which contains the value of `job_workflow_ref` from the OIDC token
> 2. `1.3.6.1.4.1.57264.1.5`, which contains the value of the `repository` claim from the OIDC token (in `org/repo` "slug" form)
> 
> These are sufficient for verification at a point in time, but some threat models may require the assertion that `org/repo` still refers to the _same_ `org` and `repo`. Fortunately, GitHub provides stable numeric identifiers for these, in the form of the `repository_id` and `repository_owner_id` claims. These can be used to detect a change in underlying account or repository identity, e.g. in the case an attacker takes over a deleted GitHub account and attempts to release malicious updates with otherwise valid-looking claims.
> 
> So, my actual suggestion: we could add two new X.509v3 extensions (and corresponding OIDs):
> 
> * `1.3.6.1.4.1.57264.1.8`: GitHub Workflow Repository ID: the stable numeric identifier for the repository the workflow was run under
> * `1.3.6.1.4.1.57264.1.9`: GitHub Workflow Repository Owner ID: the stable numeric identifier for the user or organization that owns the repository the workflow was run under

- https://github.com/moloch--/sliver-py
  - C2 CI