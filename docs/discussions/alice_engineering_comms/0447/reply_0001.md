## 2023-11-10 IETF 118 Key Transparency (KEYTRANS) Meeting

- https://datatracker.ietf.org/meeting/118/materials/agenda-118-keytrans-00
- https://datatracker.ietf.org/doc/draft-mcmillion-keytrans-architecture/
- https://notes.ietf.org/notes-ietf-118-keytrans
- Concerns about privacy
- Desire federation
- SCITT sounds like a solid option for a backing Transparency Service
- Difficult to reason about security properties without defined list of requirements
- Is there a core set of security and privacy gauntness for which all implementations are isomorphic
  - If I don't say the same thing as everyone else, everyone notices
    - KERI ADCD (Authenticated Chained Data Containers) as an implementation of SCITT sounds ideal for this, as it provides cryptographically assured duplicity detection.
- Phillip
  - Work factor
  - What are the properties of notary logs and who do they apply to keys
  - Notary chain is really a lattice
  - In Phillip's system every user and service maintains their own notary chain, therefore making it a lattice. Everything is going to link to everything because it's inherently a graph. When you want to go analyze, which notaries do you trust?
  - Phillip Hallam-Baker (in chat): That is my point. Once there is a notary log, you can use it to fix the time of any assertion you like proving it was made after the date of a particular apex and before the date of a set of apexes with dependency chains.
    - Ref: Vol 6: Time Travel with Us
- Missing sections
  - Need support for "sealed-sender"
    - Helps protect against social graph-ness of
  - Need discussion on how federation would work
  - Need discussion on privacy law compliance and detailed deletion of user data
- Current draft says requested changes are applied immediately: No need for interim inclusion proofs
  -   Benefits
    - Simplifies protocol description and operation
    - Supports deployment that want a strict KT regimen
  - Example: If you wanted you could begin using the key immediately, and check back on the log in an hours
- Daniel Huigens from Proton says they are working on deploying a KT implementation
  - https://github.com/ProtonMail
    - Golang SMTP server: https://github.com/ProtonMail/go-smtp
      - Golang IMAP server: https://github.com/ProtonMail/gluon
    - Golang RFC 5322 Internet Message Format library: https://github.com/emersion/go-message
- Everyone thanks Brendan for the work and agrees we should adopt
- Rohan says we should create a straw-person set of requirements and wrote it and put it somewhere. Simultaneously with adoption.
  - Adoption means that we agree to start work on it
  - Needs to be taken to the list regardless, everything in IETF must go through the list
- Simon Friedberger: We really need privacy guarantees within the doc, don't want people cross signing keys and leaking the social graph
- Esha Ghosh: [slides-118-keytrans-security-properties-of-key-transparency-00.pdf](https://github.com/intel/dffml/files/13317969/slides-118-keytrans-security-properties-of-key-transparency-00.pdf)
  - Verify the proofs against the latest TreeHead, alert users if proofs do not check out
  - Security Properties
    - When log operator is honest: Correctness Properties
    - We will have consistency properties when log operator behaves maliciously
  - Correctness
    - When a user looks up a key, result is the same that any other user seraching for the same key would have seen
    - When a user modifies a key, other users will be notified when it's modified
  - Consistency
    - When user looks up a key and the result is not the same results when another searching for a key would have see it will be detected
    - When a user modifies a key 
  - Consistency properties
    - Only the owner of a key will be able to say a distrubted key is fake
      - The owner will need to lookup own key in the log often
      - Each time owners key changes must check that key change has been correctly included in the log
      - Owner needs to remember ephocs they changed their key (hmmm)
- https://github.com/scitt-community/scitt-examples/pull/5
- TODO
  - [ ] Specify the privacy guarantees
  - [ ] Review compliance requirements about removing information from logs on mailing list