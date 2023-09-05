 ## 2022-11-29 @pdxjohnny Engineering Logs

- SCITT
  - Federation via DWN
    - https://github.com/TBD54566975/dwn-relay/blob/main/example/config.js
    - https://github.com/TBD54566975/dwn-sdk-js/blob/main/tests/interfaces/protocols/handlers/protocols-query.spec.ts
    - https://www.blockcore.net/platform
      - https://github.com/block-core/blockcore-vault
    - https://developer.tbd.website/projects/web5/
    - https://github.com/TBD54566975/ssi-service
      - Status reproduced below for quick reference / herstorical reference
      - > - [x] [DID Management](https://www.w3.org/TR/did-core/)
        >   - [x] [did:key](https://w3c-ccg.github.io/did-method-key/)
        >   - [ ] [did:web](https://w3c-ccg.github.io/did-method-web/)
        >   - [ ] [did:ion](https://identity.foundation/ion/)
        > - [x] [Verifiable Credential Schema](https://w3c-ccg.github.io/vc-json-schemas/v2/index.html) Management
        > - [x] [Verifiable Credential](https://www.w3.org/TR/vc-data-model) Issuance & Verification
        >   - [x] Signing and verification with [JWTs](https://w3c.github.io/vc-jwt/)
        >   - [ ] Signing and verification with [Data Integrity Proofs](https://w3c.github.io/vc-data-integrity/)
        > - [x] Applying for Verifiable Credentials using [Credential Manifest](https://identity.foundation/credential-manifest/)
        > - [ ] Requesting, Receiving, and the Validation of Verifiable Claims
        >   using [Presentation Exchange](https://identity.foundation/presentation-exchange/)
        > - [ ] Status of Verifiable Credentials using the [Status List 2021](https://w3c-ccg.github.io/vc-status-list-2021/)
        > - [ ] Creating and managing Trust documents using [Trust Establishment](https://identity.foundation/trust-establishment/)
        > - [ ] [DID Well Known Configuration](https://identity.foundation/.well-known/resources/did-configuration/) documents
- Smart Cities
  - https://www.city-chain.org/
    - https://start.city-chain.org/
      - This is pretty blockchain "coin" (a word we'll eventually forget) focused content.
    - https://github.com/sondreb this dude looks aligned
  - https://github.com/pdxjohnny/smartcities
- Threat Modeling
  - Attacks over time
    - https://www.zdnet.com/article/sha-1-collision-attacks-are-now-actually-practical-and-a-looming-danger/
- Saw article about Alex Hanna quitting due to ethical concerns, previously reached out to Blake Lemoine
  - Twitter direct message to Blake: [Rolling Alice: Forward: The Consciousness Folks](https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_forward.md#the-consciousness-folks)
  - Reaching out to DAIR
    - https://dair.ai/
      - > DAIR.AI aims to democratize Artificial Intelligence (AI) research, education, and technologies.
    - https://discord.com/channels/934159490205491311/934853197921681448
      - Whooooooaaa there buddy, This guy works for Facebook! Ruh Rough! Missalignement detected!
        - Hmmm
- Need to submit to PyCascades
  - [If You Give A Python A Computer](https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_architecting_alice/0002_shes_ariving_when.md#if-you-give-a-python-a-computer)
    - Fuck ya [Whisper](https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_architecting_alice/0004_writing_the_wave.md)

```console
$ PS1="alice@wonderland # "
```

```console
alice@wonderland # alice --help
usage: alice [-h] [-log LOG] {please,shouldi,threats,version} ...

                            .,*&&888@@#&:,
                          .:&::,...,:&#@@@#:.
                         .o,.       ..:8@@#@@+
                        .8o+,+o*+*+,+:&#@@#8@@.
                        &8&###@#&..*:8#@@#@#@@&+.
                       ,@:#@##@@8,:&#@@@###@88@@.
                      ,#@8&#@@@#o:#@@@@#8#@#8+&#.
                     +8####@@@@###@@@888#@@@#oo#.
                   .*8@###@@@@@@@@@#o*#@@#@@#8o@,
                  +###@#o8&#@@##8::##@@@&&#@8#&+
                  o@8&#&##::.,o&+88#&8##8*@@#@#,
                 .##888&&oo#&o8###8&o##8##&####8,
                .&#@8&:+o+&@@@#8#&8:8@@@@@#8@@@oo+
               ,&&#@##oo+*:@###&#88,@@@@#@o&##&8#@o,.
              ,#&###@@8:*,#o&@@@@##:&#@###*.&o++o#@@#&+
              o8&8o8@#8+,,#.88#@#&@&&#@##++*&#o&&&#@@@@.
              *88:,#8&#,o+:+@&8#:8@8&8#@@&o++,*++*+:#@@*.
              .+#:o###@8o&8*@o&o8@o888@@@o+:o*&&,@#:&@@@,
                *+&@8&#@o#8+8*#+8#+88@@@@@@&@###8##@8:*,
                  +o.@##@@@&88@*8@:8@@@@@@:.. ,8@:++.
                    +&++8@@@@##@@@@@@@@@@@+    88
                    &.   *@8@:+##o&888#@@@,   .#+
                    &.   ,@+o,.::+*+*:&#&,    ,@.
                    &.   .@8*,. ,*+++.+*     :8+
                    :+   .#@::. .8:.:**    .8@@o,
                    .o.   #@+   :@,.&*   .:@@@@@@8**.
                     +&.  :@o,+.*o,*,  .*@@@@@@@@@@#o
                   .*:&o.  8@o:,*:,  .o@@#8&&@@@@#@@@*
                 ,*:+:::o.*&8+,++  ,&@@#:  * :@@88@@@#:.
               ,::**:o:.,&*+*8:  *8@@##o   *,.8@@#8#@#@#+
              *:+*&o8:. ,o,o:8@+o@@88:*@+  +: +#@#####8##&.
            ,:&::88&,   .&:#o#@@@#,+&&*#&. .:,.&#@#88#####&,
           +::o+&8:.    :##88@@@@:.:8o+&8&. .. +8###&8&##&88*
         .:*+*.8#:    ,o*.+&@@#@8,,o8*+8##+    .+#8##8&&#8888:.
        ,:o., &#8.  .:8*.  .o, &#,*:8:+,&*:,    .8@@#o&&##8:&#8.
      .*o.*,+o8#*  +8&,  .::. .88.+:8o: ,+:,    ,o#@#8&o8##&#8+
     +o, .+,,o#8+,8@o**.,o*,  :8o +*8#*  +&,    ,*o@@#@&8&oo8&:,
    oo*+,,,*8@#..&@8:**:oo+. +8#* *+#@:...oo+  .**:8@@@ooo&:&o##+
    ::+..,++#@,.:##o&o**,....oo#++#8#@:.,:8&:.....*&@@#:oo*&oo&#@*
     .+**:*8@o,+##&o:+,,,+,,o*8#,,8@#@:,,+*o*++,,,,+&#@8*8o88&::*.
         ..8@++#@#88:,,,.,,,:+#&,,#@@#:,,.,&o*,.+++*:#@8+:*+.
            +:&8#@@##8&+,,,***@&,.8@@@*,,,.:o8&o&*o&o&o.
                 ...,*:*o&&o*8@@&o8@@@8+,,+:&&:+,...
                        o@#@@@@#@@@@@@@,.....
                        ,@##@@88#@@@@@8
                         8+.,8+..,*o#@+
                         *o  *+     #8
                          8, ,&    +@*
                          +&  &,  .@#.
                           o* ,o  o@&
                           .8. 8.,o#8
                            8. 8.,.&@:*:&@.
                           :@o:#,,o8&:o&@@.
                          .@@@@@@@@@@@#8.
                           ,*:&#@#&o*,

                                /\
                               /  \
                              Intent
                             /      \
                            /        \
                           /          \
                          /            \
                         /              \
                        /  Alice is Here \
                       /                  \
                      /                    \
                     /______________________\

             Dynamic Analysis          Static Analysis

    Alice's source code: https://github.com/intel/dffml/tree/alice/entities/alice
    How we built Alice: https://github.com/intel/dffml/tree/alice/docs/tutorials/rolling_alice
    How to extend Alice: https://github.com/intel/dffml/blob/alice/entities/alice/CONTRIBUTING.rst
    Comment to get involved: https://github.com/intel/dffml/discussions/1406
    

positional arguments:
  {please,shouldi,threats,version}

options:
  -h, --help            show this help message and exit
  -log LOG              Logging Level
```

- [Alice CLI c7dc8985fdde61459017d3fb39cb19de1f7ece2b Screenshot from 2022-11-29 21-15-40](https://user-images.githubusercontent.com/5950433/204716912-41dc0d86-86d6-4031-a2f2-fa7599ff66cd.png)

- https://colab.research.google.com/drive/1gol0M611zXP6Zpggfri-fG8JDdpMEpsI

### Thread Backup

- References
  - https://github.com/cli/cli/issues/1268

```console
$ gh api graphql -F owner='intel' -F repo='dffml' -F query=@intial_discussion_query.graphql | tee output.json | python -m json.tool | tee output.json.formated.json
$ gh gist create -p -d "$(date): https://github.com/intel/dffml/discussions/1406?sort=new https://github.com/intel/dffml/blob/alice/scripts/dump_discussion.py" output.json.formated.json scripts/dump_discussion.py
```

- TODO
  - [x] Thread backup
    - https://gist.github.com/pdxjohnny/b0b779a419c9ec7d55e1f21ff2261987
  - [ ] Fix duplicate issue creation
  - [ ] Provide alice intergrated `shouldi use` or deptool or whatever for Harsh to build off.
  - [ ] CVE Bin Tool
  - [ ] https://github.com/pdxjohnny/use-cases/blob/openssf_metrics/openssf_metrics.md after CVE Bin Tool demo, then use dataflows for arch diagrams and do the c4model conceptual upleveling
    - [ ] Review NPM RFC and mention in OpenSSF Metrics Use Case https://github.com/npm/rfcs/pull/626/files?short_path=9e1f9e7#diff-9e1f9e7b9ebe7e135d084916f727db5183eddd9bf2d9be73ca45444b6d74bfc9
      - [ ] Cross with https://scitt.io/distributing-with-oci-scitt.html
      - [ ] Ping Arsa for feedback
  - [ ] Play with entity definition conforming to https://w3c.github.io/dpv/examples/#E0027
  - [ ] Don't forget we have an *Affinity* for https://github.com/CrunchyData/pg_eventserv and how it can help with stream of consciousness / data aggregation from multiple sources and the event stream off that.
  - [x] open.intel Threat Modeling Podcast
    - [ ] Photo
    - [ ] Bio
    - [x] Enter the 36 chambers! It's the link I was looking for! (found randomly clicking on OA stuff)
      - https://github.com/intel/dffml/blob/alice/docs/arch/alice/discussion/0036/reply_0067.md
  - [ ] https://katherinedruckman.com/an-optimistic-open-source-security-qa-with-christopher-crob-robinson
  - [ ] Can we fix the CI and get Alice on here? Respond to Kate! https://www.intel.com/content/www/us/en/research/responsible-ai-publications.html
  - [ ] https://github.com/chainguard-dev/melange/pull/184/files CHADIG
  - [ ] https://github.com/intel/dffml/issues/1426
  - [ ] Need to submit to PyCascades
  - [x] Post work for the day: DEFCON 2, a non-alcoholic cocktail: Groceries, Church, Powell's. Cost: $27, not going to DEFCON 1. Priceless.