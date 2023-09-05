## 2022-11-14 SCITT Meeting Notes

- https://docs.google.com/document/d/1vf-EliXByhg5HZfgVbTqZhfaJFCmvMdQuZ4tC-Eq6wg/edit#heading=h.214jg0n2xjhp
- From Hannes Tschofenig to Everyone 08:02 AM
  - > - IoT device onboarding
    >   - https://fidoalliance.org/specs/FDO/FIDO-Device-Onboard-PS-v1.1-20220419/FIDO-Device-Onboard-PS-v1.1-20220419.html
    >   - http://www.openmobilealliance.org/release/LightweightM2M/V1_2-20201110-A/HTML-Version/OMA-TS-LightweightM2M_Core-V1_2-20201110-A.html
    >   - http://www.openmobilealliance.org/release/LightweightM2M/V1_2-20201110-A/HTML-Version/OMA-TS-LightweightM2M_Transport-V1_2-20201110-A.html
- NED IS HERE TODAY WOOHOO!!! He replied on the mailing list yesterday. John
  was stoked about that too. His involvement coming from IETF RATS to align on
  terminology is a good thing, since he's engaging in this train of thought.
  - See depth of field mapping.
- Neil
  - Involved in Inernet to identity conference
  - Interested in way tot get firm attestations from people about documents
  - Worked at Bell labs and was involved in IETF security area in the 90s
- Some refactoring needed on various docs
- Hanes's use case document used as good example for what we are trying to do
  - Need more problem statement before going into solution space.
  - Recommendation: Use laymans terms, do not use solution terminology within
    use case docs and requirements and architecture and threat model.
    - There are some overloaded terms in the architecture terminology.
  - Some attestation endorsements (signed statement about the item or asset)
    - Some overlay in terms of is it an endorsement or is it something different.
      - What is the value add that attestation is already a starting point.
      - If the use case was already written to assume the attestation use case.
    - 3rd party attestation is an endorsement in RATS
  - https://www.rfc-editor.org/rfc/rfc7744
    - Use Cases for Authentication and Authorization in Constrained Environments
    - > ```
      > Table of Contents
      >
      >    1. Introduction ....................................................4
      >       1.1. Terminology ................................................4
      >    2. Use Cases .......................................................5
      >       2.1. Container Monitoring .......................................5
      >            2.1.1. Bananas for Munich ..................................6
      >            2.1.2. Authorization Problems Summary ......................7
      >       2.2. Home Automation ............................................8
      >            2.2.1. Controlling the Smart Home Infrastructure ...........8
      >            2.2.2. Seamless Authorization ..............................8
      >            2.2.3. Remotely Letting in a Visitor .......................9
      >            2.2.4. Selling the House ...................................9
      >            2.2.5. Authorization Problems Summary ......................9
      >       2.3. Personal Health Monitoring ................................10
      >            2.3.1. John and the Heart Rate Monitor ....................11
      >            2.3.2. Authorization Problems Summary .....................12
      >       2.4. Building Automation .......................................13
      >            2.4.1. Device Life Cycle ..................................13
      >                   2.4.1.1. Installation and Commissioning ............13
      >                   2.4.1.2. Operational ...............................14
      >                   2.4.1.3. Maintenance ...............................15
      >                   2.4.1.4. Recommissioning ...........................16
      >                   2.4.1.5. Decommissioning ...........................16
      >            2.4.2. Public Safety ......................................17
      >                   2.4.2.1. A Fire Breaks Out .........................17
      >            2.4.3. Authorization Problems Summary .....................18
      >       2.5. Smart Metering ............................................19
      >            2.5.1. Drive-By Metering ..................................19
      >            2.5.2. Meshed Topology ....................................20
      >            2.5.3. Advanced Metering Infrastructure ...................20
      >            2.5.4. Authorization Problems Summary .....................21
      >       2.6. Sports and Entertainment ..................................22
      >            2.6.1. Dynamically Connecting Smart Sports Equipment ......22
      >            2.6.2. Authorization Problems Summary .....................23
      >       2.7. Industrial Control Systems ................................23
      >            2.7.1. Oil Platform Control ...............................23
      >            2.7.2. Authorization Problems Summary .....................24
      >    3. Security Considerations ........................................24
      >       3.1. Attacks ...................................................25
      >       3.2. Configuration of Access Permissions .......................26
      >       3.3. Authorization Considerations ..............................26
      >       3.4. Proxies ...................................................28
      >    4. Privacy Considerations .........................................28
      >    5. Informative References .........................................28
      >    Acknowledgments ...................................................29
      >    Authors' Addresses ................................................30
      > ```
- We need to address Ned's Concern to define what is the clear scope of the difference
  between what IETF RATS attestation offers.
- Sylvan
  - Concete senario using confideniation conpute
  - Using hardware attestiaont reprots abou CCF running in the cloud
  - Say you're running a workload you are running it in the cloud
    - Covidential containers which covers the VMs, hostdata MRconfig, policy used to say what you can run on that utility VM, it has a hardware attestqation story and follow the RATs spec.
    - This can be passed out to anyone to verify and validate the workload is what it was based on measurment
  - Now you don't want a precisou hash of mrenclave on TXD, it's fine to run whatever as long as it's signed by a specific issuer, that given endoresements, I might be handed a signature on an image the provider might give a different signed image to someone elese, what SCITT does (verifter policy, UVM hash percides SCITT receipt valation and feed for UVM which is the feed that identifies its purpose, from this parent on this __ of this scitt image, expect the payload in COSE.1 to be the hash that you would find measured from the TPM
  - I want to be able to attest container application, webaps, whatever
    - Can the attestation not report on that?
    - Sylvan has a parcitular view on how you report on the confidential containre and how it attests to the workload
      - If we want to talk just about the base VM boot image, how do I make sure my provider can give me version 1.2 without breaking my workload and I get transparency over every workload that can run (policy) and I have recpeits of it happening
      - As a verifier you only want to use a service if it's running code I crea bout
        - If I trust an abitrary signer, then I can rely on signature alone
        - But if I want SCITT, it's because I want auditable evidence then I want a recpeit that is universally verifiable, you can hand it off to customers to prove that I ran in a confidential compute environemnt.
          - Ned says why do I need that? I have the precise hashs?
            - We have a post hoc auditability gaurintee because it's transparence
- RATS
  - Reference value providers
  - Verifier's job is to do a mapping between the two
    - The endorsement is a claim that is true if the reference value is matched to evidence
    - Those cliams might be added to accpted set if there was some Notary specific data
  - Verifier has a policy that says I trust this endorser and I don't trust that one.
  - SCITT Transparency is one thing we layer on top
  - By binding endorsers though audit log we allow for online detection, but most people might do it after the fact (post-hoc, ad-hoc post?)
- Attestation letter will be defined by CISA, this will become an artifact the customer will receive
  - How could they do that using RATS?
    - An attestation letter in this case sounds more like an endorsement (I'm a good guy, trust me, these are the things that I do)
      - SW vendor makes a claim, customer needs to be able to verify the trustworthyness of that claim
        - ISO9000, he I'm following this process, are there auditors to make sure you're following it?
          - Customers might go to SCITT and say has anyone looked at this thing? Is it trustworthy?
            - This is why DFFML cares about SCITT, because of adding data about development lifecycle processes to act as a self audit capability for people to run different static analysis (meta static analysis)
            - Is there a blocking process to get on the regisistry? no! (federation, DID based flat file, we can build all this offline and join disparate roots later, this is why we like SCITT)
              - Other parties can endorse and make transparnt their endorsements (notary step)
              - Registration policy controls what signed statemtnst can be made transparent, it can alos say who can put signed statemtenst in (OIDC) and make them transparent via this instance
              - We want to enable additional audutors to audit each other, they make additional statemtnst, sign those statemtnst and make them transpacent via the SCITT log they submit to
              - This allows us to go N level and N link on the graph deep in terms of what set we want to define we "trusted"
- SW produces package
  - 3rd party produces endorsement about produced package (a 2nd witness of that claim)
    - Ned says this is possible with RATS, the thing it doesn't try to define is that you
      have to have that, they would call that an "appraisal policy", the you have to have
      this second entity (Alice? ;) doing the tests.
    - SCITT is saying those claims have to be published somewhere (even self with Alice
      offline case).
      - What value do those additional witnesses bring?
        - Existance of a recpeit is proof that signed claims were made and made in a
          specific order, they are tamperproof (rather than just tampter evident).
        - With transpanecy I can accept an update, and know I can check later,
          if they lie, I can go find out that they lied.
- TODO
  - [ ] Section on Federation (8)
    - [SCITT API Emulator Bring Up](https://github.com/intel/dffml/discussions/1406?sort=new#discussioncomment-4110695)
      - We upload `alice shouldi contribute` dataflow to SCITT and get a receipt!
        - Friends, today is a great day. :railway_track:
        - Next stop, serialization / federation with Alice / Open Architecture serialization data flow as SCITT service.
          - Started with mermaid added in https://github.com/intel/dffml/commit/fbcbc86b5c52932bccf4cd6321f4e79f60ad3023 to https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_architecting_alice/0002_shes_ariving_when.md
  - [ ] Use case documents
    - [ ] OpenSSF Metrics
      - Use Microsoft SCITT API Emulator (MIT) as upstream / reference
        implementation. Talk about how to used the data provenance on the workflow
        (`alice shouldi contribute`).
        - We can then start doing the `did:merkle:` what do I care about itermediate
          representation to do cross platform (jenkins, github actions, etc.) caching
          / analysis of caching / please contributed streamlined.
          - Play with OIDC and SCITT
        - Later show overlayed flow on top of upstream (OpenSSF metrics or something
          ideally would be the upstream defining these flows, probably, in most cases).
          - Need to patch dataflows to include `upstream` as flows / system context
            it came from if overlayed.