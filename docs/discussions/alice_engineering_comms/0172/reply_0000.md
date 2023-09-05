## 2023-02-08 @pdxjohnny Engineering Logs

```console
$ curl -sfL https://vcs.activitypub.securitytxt.dffml.chadig.com/push/outbox | jq --unbuffered -r '.orderedItems[].object.content' | wc -l
5277
$ curl -sfL https://vcs.activitypub.securitytxt.dffml.chadig.com/push/outbox | jq --unbuffered -r '.orderedItems[].object.content' | grep stream_of | grep modified | jq -r --unbuffered '.commits[].modified[]'
docs/tutorials/rolling_alice/0000_architecting_alice/0005_stream_of_consciousness.md
jq: error (at <stdin>:2): Cannot iterate over null (null)
docs/tutorials/rolling_alice/0000_architecting_alice/0005_stream_of_consciousness.md
jq: error (at <stdin>:4): Cannot iterate over null (null)
jq: error (at <stdin>:5): Cannot iterate over null (null)
jq: error (at <stdin>:6): Cannot iterate over null (null)
$ curl -sfL https://vcs.activitypub.securitytxt.dffml.chadig.com/push/outbox | jq --unbuffered -r '.orderedItems[].object.content' | grep stream_of | grep modified | jq -r --unbuffered '.commits[].modified[]' 2>/dev/null
docs/tutorials/rolling_alice/0000_architecting_alice/0005_stream_of_consciousness.md
docs/tutorials/rolling_alice/0000_architecting_alice/0005_stream_of_consciousness.md
$ curl -sfL https://vcs.activitypub.securitytxt.dffml.chadig.com/push/outbox | jq --unbuffered -r '.orderedItems[].object.content' | grep modified | jq -r --unbuffered '.commits[].modified[]' 2>/dev/null
docs/tutorials/rolling_alice/0000_architecting_alice/0005_stream_of_consciousness.md
entities/alice/alice/shouldi/contribute/cicd.py
docs/tutorials/rolling_alice/0000_architecting_alice/0005_stream_of_consciousness.md
operations/innersource/dffml_operations_innersource/operations.py
.github/workflows/build_images_containers.yml
operations/innersource/dffml_operations_innersource/npm_groovy_lint.py
```

- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue
- https://doi.org/10.1016/j.ejor.2020.12.054
  - Supply chain game theory network modeling under labor constraints: Applications to the Covid-19 pandemic
    - https://intel.github.io/dffml/main/examples/or_covid_data_by_county.html
  - > we construct a supply chain game theory network framework that captures labor constraints under three different scenarios. The appropriate equilibrium constructs are defined
    > ![Screenshot_20230208-054700_of_conclousion_of_paper_on_supply_chains](https://user-images.githubusercontent.com/5950433/217573307-c85cc3ef-c63f-4bb3-be42-ece63cb602fe.png)
  - They are in alignment that a general equilibrium model would be fun
- https://universeodon.com/@georgetakei/109824609861703097
  - https://github.com/intel/dffml/commit/4ef226e2ecd384560d635fa84036003b525ad399 [💊](https://pdxjohnny.github.io/redpill/)
  - https://mastodon.social/@pdxjohnny/109456014313438341
  - https://github.com/intel/dffml/tree/alice/docs/arch/alice/discussion/0001/reply_0006.md
  - > Someone asked ChapGPt to come up with 10 Commandments for the modern world. I could be guided by these principles. Perhaps a new religion is in order?
    > ![9e3ac5f3049ee319](https://user-images.githubusercontent.com/5950433/217577363-83e0bcc8-6886-4d01-bce5-dc48d8a31651.png)
- https://intel.github.io/dffml/main/plugins/service/http/cli.html#sources
- https://intel.github.io/dffml/main/plugins/service/http/api.html#id6
- Kent Beck - Tidy First
  - > The motto of Empirical Software Design is (repeat after me), “Software design is an exercise in human relationships.” 
- TODO
  - [x] Clean CI run
    - [ ] Re-enable failing tests after debug
      - #1436
        - #1361