These are the engineering logs of entities working on Alice. If you
work on [Alice](https://github.com/intel/dffml/tree/alice/docs/tutorials/rolling_alice/0000_architecting_alice#what-is-alice) please use this thread as a way to communicate to others
what you are working on. Each day has a log entry. Comment with your
thoughts, activities, planning, etc. related to the development of
Alice, our open source artificial general intelligence.

This thread is used as a communication mechanism for engineers so that
others can have full context around why entities did what they did
during their development process. This development lifecycle data helps
us understand more about why decisions were made when we re-read the
code in the future (via cross referencing commit dates with dates in
engineering logs). In this way we facilitate communication across
both time and space! Simply by writing things down. We live an an
asynchronous world. Let's communicate like it.

We are collaboratively documenting strategy and implementation as
living documentation to help community communicate amongst itself
and facilitate sync with potential users / other communities /
aligned workstreams.

- Game plan
  - [Move fast, fix things](https://hbr.org/2019/01/the-era-of-move-fast-and-break-things-is-over). [Live off the land](https://www.crowdstrike.com/cybersecurity-101/living-off-the-land-attacks-lotl/). [Failure is not an option](https://github.com/intel/dffml/tree/alice/docs/tutorials/rolling_alice/0000_architecting_alice#the-scary-part).
- References
  - [Video: General 5 minute intro to Alice](https://www.youtube.com/watch?v=THKMfJpPt8I?t=129&list=PLtzAOVTpO2jYt71umwc-ze6OmwwCIMnLw)
  - https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_forward.md
  - https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_preface.md
  - https://gist.github.com/07b8c7b4a9e05579921aa3cc8aed4866
    - Progress Report Transcripts
  - https://github.com/intel/dffml/tree/alice/entities/alice/
  - https://github.com/intel/dffml/tree/alice/docs/tutorials/rolling_alice/0000_architecting_alice#what-is-alice
  - https://github.com/intel/dffml/pull/1401
    - https://github.com/intel/dffml/pull/1207
    - https://github.com/intel/dffml/pull/1061
  - #1315
  - #1287
  - Aligned threads elsewhere (in order of appearance)
    - @dffml
      - [DFFML Weekly Sync Meeting Minutes](https://docs.google.com/document/d/16u9Tev3O0CcUDe2nfikHmrO3Xnd4ASJ45myFgQLpvzM/edit)
        - Alice isn't mentioned here but the 2nd party work is, Alice will be our maintainer who helps us with the 2nd party ecosystem.
      - #1369
    - @pdxjohnny
      - https://twitter.com/pdxjohnny/status/1522345950013845504
      - https://mastodon.social/@pdxjohnny/109320563491316354
  - [Google Drive: AliceIsHere](https://drive.google.com/drive/folders/1E8tZT15DNjd13jVR6xqsblgLvwTZZo_f)
    - Supplementary resources, status update slide decks, cards (with instructions of how to get more printed), Entity Analysis Trinity drawio files, screenshots. Miscellaneous other files.
  - async comms / asynchronous communications
    - https://twitter.com/SergioRocks/status/1579110239408095232

## Engineering Log Process

- Alice, every day at 7 AM in Portland's timezone create a system context (the tick)
  - Merge with existing system context looked up from querying this thread if exists
    - In the future we will Alice will create and update system contexts.
      - We'll start with each day, then move to a week, then a fortnight, then 2 fortnights.
      - She'll parse the markdown document to rebuild the system context as if it's cached
        right before it would be synthesized to markdown, we then run updates and trigger
        update of the comment body. Eventually we won't use GitHub and just DID based stuff.
        We'll treat these all as trains of thought / chains of system contexts / state of the
        art fields.
        - Take a set of system contexts as training data
        - The system context which we visualize as a line dropped from the peak of a pyramid
          where it falls through the base.
        - We use cross domain conceptual mapping to align system contexts in a similar direction
          and drop ones which do are unhelpful, do not make the classification for "good"
        - What remains from our circular graph is a pyramid with the correct decisions
          (per prioritizer) 
        - This line represents the "state of the art", the remembered (direct lookup) or
          predicted/inferred system contexts along this line are well rounded examples of
          where the field is headed, per upstream and overlay defined strategic plans
          and strategic principles
          - References:
            - `$ git grep -C 5 -i principle -- docs/arch/`
              - Source: https://github.com/intel/dffml/discussions/1369
  - Inputs
    - `date`
      - Type: `Union[str, Date]`
      - Example: `2022-07-18`
      - Default: `did:oa:architype:current-date`
   - Add yesterdays unfinished TODO items to this train of though with the 
   - Create a document (docutils?)
     - Make the top level header `date` with "Notes" appended
     - Collect all previous days TODOs from within the individual entity comments within the thread for the days comment (the team summary for that day)
       - Drop any completed or struck through TODOs
       - Output a list item "TODO" with the underlying bullets with handle prepended and then the TODO contents
         - Create comments for individuals after this the current system context is posted and we have a live handle to it to reply with each individuals markdown document.
   - Synthesis the document to markdown (there is a python lib out there that can do docutils to md, can't remember the name right now)
   - Upsert comment in thread
- Any time (it's a game)
  - We find something we need to complete #1369 that was just completed by someone else
    - Paste `![chaos-for-the-chaos-god](https://user-images.githubusercontent.com/5950433/220794351-4611804a-ac72-47aa-8954-cdb3c10d6a5b.jpg)`
    - chaos: diversity of authorship applied to clustering model run on all thoughts (dataflows) where each dataflow maps to line changed and the cluster classification is the author.
      - https://github.com/intel/dffml/issues/1315#issuecomment-1066814280
  - We accelerate a train of thought
    - Paste 🛤️
  - We use manifests or containers
    - Paste all the things meme `![oci-all-the-things](https://user-images.githubusercontent.com/5950433/222979759-0dd374b2-ee5f-4cbc-92d1-5cb8de078ee8.png)`
  - We find more ways to on-ramp data to the hypergraph
    - `![knowledge-graphs-for-the-knowledge-god](https://user-images.githubusercontent.com/5950433/222981558-0b50593a-c83f-4c6c-9aff-1b553403eac7.png)`
  - We do a live demo
    - `![live-demo-for-the-live-demo-god](https://user-images.githubusercontent.com/5950433/226699339-45b82b38-a7fc-4f2f-a858-e52ee5a6983d.png)`
  - We see alignment happening
    - `![such-alignment](https://user-images.githubusercontent.com/5950433/226707682-cfa8dbff-0908-4a34-8540-de729c62512f.png)`
  - We enable bisection or hermetic or cacheable builds
    - `![hash-values-everywhere](https://user-images.githubusercontent.com/5950433/230648803-c0765d60-bf9a-474a-b67e-4b4177dcb15c.png)`
