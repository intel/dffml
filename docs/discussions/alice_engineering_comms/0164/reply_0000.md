## 2023-01-31 @pdxjohnny Engineering Logs

- Release of OpenVEX! Chaos smiles on us again :)
  - https://mastodon.social/@ariadne@treehouse.systems/109784681116604896
    - > meanwhile at work, a thing i've been working on for the past few months has dropped: https://www.chainguard.dev/unchained/accelerate-vex-adoption-through-openvex it's basically like ActivityStreams, but for security vulnerability data sharing. with a little bit of work, we can lift up to something more like ActivityPub for real-time collaboration, a blog is forthcoming about it.
  - https://github.com/openvex/spec/blob/main/ATTESTING.md#digital-signatures
  - https://github.com/pdxjohnny/activitypubsecuritytxt/commit/9a68cb0b752126046157b047cb72563228c078de
  - https://github.com/pdxjohnny/activitypubsecuritytxt/commit/1e35f549a33347918335e89200055841b267e86c
    - https://github.com/openvex/spec/blob/main/OPENVEX-SPEC.md#openvex-and-json-ld

![chaos_for_the_chaos_God](https://user-images.githubusercontent.com/5950433/215828966-0f91a8fe-0809-4523-9202-b09fd5f635d9.jpg)

- https://github.com/fuzhibo/jekyll-mermaid-diagrams/blob/b5e0c37486dec1c840d6e8a47c92a754af3cfd72/lib/jekyll-mermaid-diagrams.rb#L14-L15
- https://hachyderm.io/@holly_cummins/109636163544669034
  - > TIL there's a technical name for why ideas happen in the shower: the "default mode network" is a pattern of brain activity, measurable using fMRI, that happens when we're unfocussed. When the brain goes into idle mode (reduced activity), this part of the brain actually becomes *more* active. What does the default mode network do? Research is ongoing, but part of it definitely seems to be making connections, which is associated with *curiosity and creativity*. More here: [https://www.nationalgeographic.co.uk/histo](https://www.nationalgeographic.co.uk/history-and-civilisation/2022/08/the-science-of-why-you-have-great-ideas-in-the-shower)
  - grep rhe system requires excersize
  - Chaos metric
- A wild manifest appears!
  - https://github.com/openvex/vexctl#3-vexing-a-results-set
  - https://github.com/intel/dffml/blob/alice/docs/arch/0008-Manifest.md

![image](https://user-images.githubusercontent.com/5950433/215843365-9a03f49f-2607-4e48-acd0-21269814427d.png)

- https://github.com/microsoft/GODEL
  - http://ndjson.org/
    - `--train_file`
  - https://gist.github.com/pdxjohnny/016f8d9edcb65f62c3fbe4b019299ef7
    - https://colab.research.google.com/gist/pdxjohnny/09a125f58151b5099cbff02b27a80abb/finetunegodel.ipynb
      - https://til.simonwillison.net/python/gtr-t5-large
  - https://ipython.readthedocs.io/en/stable/interactive/magics.html
  - https://ipython.readthedocs.io/en/stable/interactive/magics.html#cell-magics
    - https://github.com/ipython/ipython/issues/13376
- https://slsa.dev/spec/v0.1/levels
- https://global-power-plants.datasettes.com/global-power-plants/global-power-plants?owner=PacifiCorp
  - Inventory
    - #1207
    - https://lite.datasette.io/
    - https://docs.datasette.io/en/stable/getting_started.html#using-datasette-on-your-own-computer
      - sqlite to endpoint
      - Could maybe do linked data?
        - Could we go from CVE Bin Tool database (`--nolock`) to OpenVEX via a plugin for datasette?
        - Could we loop againt the db with nolock to publish events during scan from seperate process? Would have to do db writes more often?
          - https://www.sqlite.org/wal.html
          - https://datasette.io/plugins/datasette-scraper#user-content-usage-notes