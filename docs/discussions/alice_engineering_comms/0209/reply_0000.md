## 2023-03-16 @pdxjohnny Engineering Logs

- https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/redis.html
  - We can feed data from the websocat into redis and use celery to kick off Alice
  - https://docs.github.com/en/actions/using-containerized-services/creating-redis-service-containers
    - This works for public GitHub runners, which we are using for OSS scanning. We may need tweaks for our OS DecentrAlice on DigitalOcean/DevCloud setup
  - Then we can run matrix jobs which process incoming vulns to mitigate or analyze
- https://github.com/ossf/wg-vulnerability-disclosures/discussions/127#discussioncomment-5335373 (Jason's relevant comments below)
  - > What the US government decides to do or not do is not my primary concern. I am trying to make the entire industry work better, to protect society - not just the US government. To do that requires us to work together, not fight each other over silly issues like "heaviness" of JSON formats that we want to be consumed by machines and never even read by a human.
    >
    > The whole VDR vs VEX thing I think is just needless additional confusion. When you take the technical implementations out of the mix, and just read what a VDR is and read what a VEX is, they are trying to do exactly the same thing, and it is all just semantics. You can actually use VEX to create a VDR - this is actually what CycloneDX is doing today. IMO, NIST did the industry a disservice inventing & pushing a new word for a concept that already existed. The ISO standard for VDR is also lacking 1/2 of VEX because it does not give a simple way to say 'I am not susceptible to this vulnerability, and here is why', which is a primary use case of VEX. however ironically, if you read the NIST best practice - they actually suggest this information be part of a VDR! IE - when you actually read all the text - the ISO minimal fields for VDR do not even meet what NIST is asking for... NIST VDR actually asks for a VEX! It is so needlessly confusing.
  - > VEX contains both positive and negative assertions - just like a "VDR" does... I suggest you re-watch the video you linked because it is actually discussed, with an example. Again, no need to argue about this because none of it is worth arguing about. I know & respect both Allan and Thomas - but neither of them "owns" the definition of VEX, neither does OASIS, or anyone else. VEX is just a concept. Just like VDR is just concept, it is a best practice that NIST published in a document - these are abstract ideas, neither of them are standards. No one "owns" the definitions of these things, there is no NIST publication that officially defines what a VDR is... if there is, please share it. Simmilarly, there is no standards body at all that defines what a VEX is, CISA is looking to publish some guidelines, but CISA is not a standards body either so whatever gets published still won't define 'VEX' as a thing, it will simply define a CISA point of view. Anyone can claim anything is a VEX, because no one can say otherwise right now.
  - Bingo
- ActivityPub security.txt/md mermaid where are you? 🧜‍♀️
  - https://cdn.jsdelivr.net/npm/mermaid@10.0.2/dist/mermaid.esm.min.mjs
  - https://github.com/mermaid-js/mermaid/blob/b5a4cc0e17168c257a3b0d40a068e3addfc9c40a/packages/mermaid/src/docs.mts#L51
  - https://cdn.jsdelivr.net/npm/mermaid@10.0.2/
  - https://cdn.jsdelivr.net/npm/mermaid@9.3.0/dist/mermaid.min.js
    - https://cdn.jsdelivr.net/npm/mermaid@10.0.2/dist/mermaid.min.js
      - 10.0.2 does not have non-`import` js
      - https://www.jsdelivr.com/package/npm/mermaid?tab=stats&path=dist
- https://github.com/executablebooks/rst-to-myst
  - https://myst-parser.readthedocs.io/en/latest/apidocs/myst_parser/myst_parser.mdit_to_docutils.html
  - https://myst-parser.readthedocs.io/en/latest/syntax/optional.html#task-lists
  - For our notebook conversion
    - #1392