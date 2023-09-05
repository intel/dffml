## Overlays as Dynamic Context Aware Branches

> Todo more fanciful tutorial name

At a minimum it's like saying when I checkout this branch I want you to cherry pick these commits (semanticly?) from these other branches (and run A/B cross validation of course) and make that a sort of virtual branch where those commits are applied and still tracked as dev or in flight or just alternately sourced versions.

- References
  - https://github.com/intel/dffml/issues/1315#issuecomment-1066971630
    - Alice and Bob working on CR0/4
  - Examples of virtual branches
    - Turning on debug logging while working on NVD style API for use by
      cve-bin-tool (and Alice of course).
      - [2022-11-18 @pdxjohnny Engineering Logs](https://github.com/intel/dffml/discussions/1406?sort=new#discussioncomment-4177910)
- TODO
  - Knowledge graph of manifests with SCITT receipts
    - Stream of Consciousness
      - We share test results of cross validation and virtual branch node additions here
  - Alice, Bob, and Eve working with three separate repos
    - Cross validation comes into play here