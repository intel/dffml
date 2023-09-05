## 2022-11-22 @pdxjohnny Engineering Logs

- https://www.science.org/doi/10.1126/science.ade9097
  - Some people did the diplomacy civ style thing
    - grep `docs/arch/alice/discussion` thread
  - https://youtu.be/u5192bvUS7k
  - https://twitter.com/ml_perception/status/1595070353063424000
- Rebased in cve-bin-tool@main to [nvd_api_v2_tests](https://github.com/pdxjohnny/cve-bin-tool/compare/nvd_api_v2_tests) in pursuit of https://github.com/intel/cve-bin-tool/issues/2334

[![asciicast](https://asciinema.org/a/539495.svg)](https://asciinema.org/a/539495)

- https://github.com/OR13/didme.me/issues/18
  - https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_architecting_alice/0007_an_image.md
- https://twitter.com/tlodderstedt/status/1592641414504280064
  - https://openid.net/openid4vc/
    - OpenID for Verifiable Credentials (OpenID4VC)
  - https://www.slideshare.net/TorstenLodderstedt/openid-for-verifiable-credentials-iiw-35
  - https://openid.bitbucket.io/connect/openid-connect-self-issued-v2-1_0.html#name-sharing-claims-eg-vc-from-s
    - The following quotes are applicable to our DFFML CI/CD setup.
      We care about static analysis results and stuff (`alice shouldi`),
      for example auth of our runners (grep OSS scanning) and artifacts
      to push data to `data.chadig|nahdig.com` and then to the OpenSSF.
      - Ideally our data structures are self identifying and authing (UCAN, ATP, etc.)
      - We still need bridges into existing identity and auth infra
        - [DID + HSM Supply Chain Security Mitigation Option](https://github.com/intel/dffml/tree/alice/docs/arch/0007-A-GitHub-Public-Bey-and-TPM-Based-Supply-Chain-Security-Mitigation-Option.rst)
        - https://www.youtube.com/clip/Ugkxf-HtFY6sR_-EnGGksIik8eyAKQACE0_n?list=PLtzAOVTpO2jaHsS4o-sDzDyHEug-1KRbK
          - Vision: Reducing Overhead via Thought Communication Protocol
            - https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_architecting_alice/0005_stream_of_consciousness.md
            - [2022-10-15 Engineering Logs: Rolling Alice: Architecting Alice: Thought Communication Protocol Case Study: DFFML](https://github.com/intel/dffml/discussions/1406?sort=new#discussioncomment-3883683)
          - The video this was clipped from was linked in the commit message https://github.com/intel/dffml/commit/fc42d5bc756b96c36d14e7f620f9d37bc5e4a7fd
          - Found the previous stream of consciousness aligned with this. I had been meaning to look for it, we'll be back in this train of thought when we get to didme.me "An Image" python implementation.
            - https://www.youtube.com/watch?v=9y7d3RsXkbA&list=PLtzAOVTpO2jaHsS4o-sDzDyHEug-1KRbK
    - > [2.4. ](https://openid.bitbucket.io/connect/openid-connect-self-issued-v2-1_0.html#section-2.4)[Sharing Claims (e.g. VC) from Several Issuers in One Transaction](https://openid.bitbucket.io/connect/openid-connect-self-issued-v2-1_0.html#name-sharing-claims-eg-vc-from-s)
When End-Users apply to open a banking account online, in most countries, they are required to submit scanned versions of the required documents. These documents are usually issued by different authorities, and are hard to verify in a digital form. A Self-issued OP directly representing the End-User may have access to a greater set of such information for example in the format of Verifiable Credentials, while a traditional OP may not have a business relationship which enables access to such a breadth of information. Self-Issued OPs could aggregate claims from multiple sources, potentially in multiple formats, then release them within a single transaction to a Relying Party. The Relying Party can then verify the authenticity of the information to make the necessary business decisions.
  - https://openid.net/wordpress-content/uploads/2022/06/OIDF-Whitepaper_OpenID-for-Verifiable-Credentials-V2_2022-06-23.pdf
    - > OpenID Connect, a protocol that enables deployment of federated Identity at scale, was built with User-Centricity in mind. The protocol is designed so that the Identity Provider releases the claims about the End-User to the Relying Party after obtaining consent directly from an EndUser. This enables Identity Providers to enforce consent as the lawful basis for the presentation based on the Relying Party’s privacy notice. The protocol also enables two kinds of Identity Providers, those controlled by the End-Users and those provided by the third parties. Now, User-Centricity is evolving to grant the End-Users more control, privacy and portability over their identity information. Using OpenID for Verifiable Credentials protocols, the End-Users can now directly present identity information to the Relying Parties. This empowers the EndUsers to retain more control over the critical decisions when and what information they are sharing. Furthermore, the End-Users’ privacy is preserved since Identity Providers no longer know what activity the End-Users are performing at which Relying Party. End-Users also gain portability of their identity information because it can now be presented to the Relying Parties who do not have a federated relationship with the Credential Issuer. Then the technical details of OpenID4VC are presented, alongside an explanation of certain decision choices that were made, such as why OpenID Connect, and OAuth 2.0 are well-suited as basis for presentation and issuance protocols for verifiable credentials. Finally, the whitepaper concludes by reiterating the importance of making choices for standards that meet certain use-cases in order to realize a globally interoperable verifiable credentials ecosystem. Achieving large-scale adoption of verifiable credentials will be "by Evolution, not by Revolution". The identity community can more swiftly empower people, and government authorities developing identity infrastructure and policies, by adopting standards like OpenID4VC that facilitate convergence and interoperation of existing and emerging standards.
- https://vos.openlinksw.com/owiki/wiki/VOS/VOSIntro
- https://github.com/OpenLinkSoftware/OSDS_extension
- https://hobbit-project.github.io/
- https://youtube.com/clip/Ugkxf-HtFY6sR_-EnGGksIik8eyAKQACE0_n
  - Vision: Reducing Overhead via Thought Communication Protocol
- https://cloud.hasura.io/public/graphiql?header=content-type:application/json&endpoint=https://api.graphql.jobs
- We're working on fixing the CI right now
  - The vuln serving `NVDStyle` is our base for comms right now (think manifests)
    - https://github.com/intel/dffml/blob/alice/docs/arch/0008-Manifest.md
    - This is how we will be facilitating Continuous Delivery.
      - Open source projects will implement vuln stream handling, we are
        hopefully piggy backing our `FROM` rebuild chain and so forth on top,
        once again, we're always looking for reliable resilient ubiquitously
        available comms. Reuse, reuse, reuse.
- https://github.com/intel/dffml/issues/1421
- Found some meetups to share Alice with
- https://www.meetup.com/rainsec/events/289349686/
  - > RainSec - PDX Information Security Meetup: RainSec is an informal group of like-minded security professionals who meet to network and discuss topics of interest in a non-work, non-vendor setting. While our target audience is experienced information security professionals, this is a public event open to any interested parties. If you have a friend or colleague who might benefit, please pass an invite along.
- https://www.meetup.com/hardware-happy-hour-3h-portland/events/289759128/
  - > Hardware Happy Hour is an informal way to socialize, show off your projects, and talk about the world of hardware.
- https://www.meetup.com/ctrl-h/events/282093316/
  - > Dorkbot PDX (Virtual): Part virtual hackathon, part virtual geek social, these virtual biweekly meetings are a time for you to virtually join others for insight, inspiration or just insanity.
  - https://app.gather.town/app/1KLgyeL4yGzBeCAL/dorkbot
- https://app.gather.town/app
  - UX wow. Landing into anon profile allowing actions / creation. Love it.
- https://mastodon.online/@rjh/109388793314837723
  - > nsrllookup.com is back online after a long pandemic-related hiatus.  If you need to sort wheat from chaff for large volumes of data, try removing every piece of data in NIST's collection.
    >
    > Many thanks to [@warthog9](https://mastodon.social/@warthog9@social.afront.org) for hosting nsrllookup.com all these years.  :)
  - https://github.com/rjhansen/nsrlsvr
  - We should hybridize this with SCITT recpeits returned for the content addresses, let's use SHA384 or something stronger
  - https://mastodon.online/@rjh/109388812626470845
    - Let's use this hybrid with the NVDStyle API, or perhaps let's wait (8 minutes ago, Chaos smiles on us again ;) Really we should stick with OCI registry on our first pass here.
      - > Work on version 2 of nsrllookup is well underway. When I originally developed it, I elected to write my own very simple wire protocol. Although it still works fine, it means whenever I want to write a binding for a new programming language I have to rewrite the parser-generator.
        >
        > Version 2, currently underway, moves to gRPC.  This should make it much easier to integrate with third-party tools like Autopsy.
- Random LOL
  - Architecting Alice: Volume 0: Context: Part 1: Where are we: YouTube's automated captions: "Intro, The Plan, Alice, Chaos, Nested Virtualization"
    - Hit the nail on the head with that one ;P

[![Architecting Alice: Volume 0: Context: Part 1: Where are we: YouTube's automated captions LOL: "Intro, The Plan, Alice, Chaos, Nested Virtualization"](https://user-images.githubusercontent.com/5950433/203405118-91f1d2d8-a9f7-42e8-a468-d984e7f7d7ae.png)](https://www.youtube.com/watch?v=dI1oGv7K21A&list=PLtzAOVTpO2jaHsS4o-sDzDyHEug-1KRbK)

- https://docs.velociraptor.app/
- https://www.thc.org/segfault/
  - https://github.com/hackerschoice/segfault
  - Stoooooked
- https://www.thc.org
- https://www.gsocket.io/
  - Doooooooooope
  - Let's see if there's a cross with DERP here, Wireguard is probably involved.
  - > [![gsocket-asciicast](https://asciinema.org/a/lL94Vsjz8JM0hCjnfKM173Ong.svg)](https://asciinema.org/a/lL94Vsjz8JM0hCjnfKM173Ong)
- https://github.com/vanhauser-thc/
- TODO
  - [ ] Finish https://github.com/intel/cve-bin-tool/issues/2334
    - https://github.com/intel/cve-bin-tool/pull/2384