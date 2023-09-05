## 2023-01-06 @pdxjohnny Engineering Logs

- Fixing CI container builds and tests
- The SHA384 on tokei v10.1.1 changed... WTF?
  - This usually means something is wrong with the download code (I just changed to add chmod) and move return statement... or EITM (Entity In The Middle attack)...
- https://proceedings.neurips.cc/paper/2017/file/3f5ee243547dee91fbd053c1c4a845aa-Paper.pdf
  - Attention is All You Need
  - https://paperswithcode.com/paper/attention-is-all-you-need
    - GitHub search
      - https://github.com/tensorflow/tensor2tensor/blob/5623deb79cfcd28f8f8c5463b58b5bd76a81fd0d/docs/walkthrough.md#walkthrough
      - https://github.com/tensorflow/tensor2tensor/blob/3817e96deda6f3fdada4fedcd5efe33ed0438485/tensor2tensor/models/transformer.py#L22
- TODO
  - [ ] Listen to podcast with Katherine and Dan Lorc
    - https://twit.tv/shows/floss-weekly/episodes/712
  - [ ] https://docs.sigopt.com/core-module-api-references/get_started
    - https://github.com/sigopt/sigopt-python
    - This could be good to add to the backlog to make wrappers / plugins for