## 2022-11-30 @pdxjohnny Engineering Logs

- https://unix.stackexchange.com/questions/501577/if-else-in-jq-is-not-giving-expected-output
- https://twitter.com/SergioRocks/status/1597592532992532480
  - This dude Sergio really does rock! :metal:
  - The Alice Initiative is all about scaling knowledge transfer!
- For posterity: [screenshot-of-ories-stable-diffusion-cyberpunk-archiver-ethical-ml](https://user-images.githubusercontent.com/5950433/204817902-684a4385-5197-456a-8910-2b2b41a16c5b.jpg)
  - If time is relative then timing really is everything isn't it, it's all just a delta
- https://github.com/intel/dffml/commit/7f6aa4a4155420b5354ba6384f128a2f7f8d6605
  - https://en.wikipedia.org/wiki/Jam_tomorrow
    - > "I'm sure I'll take you with pleasure!" the Queen said. "Two pence a week, and jam every other day."
      > Alice couldn't help laughing, as she said, "I don't want you to hire me – and I don't care for jam."
      > "It's very good jam," said the Queen.
      > "Well, I don't want any to-day, at any rate."
      > "You couldn't have it if you did want it," the Queen said. "The rule is, jam to-morrow and jam yesterday – but never jam to-day."
      > "It must come sometimes to 'jam to-day'," Alice objected.
      > "No, it can't," said the Queen. "It's jam every other day: to-day isn't any other day, you know."
      > "I don't understand you," said Alice. "It's dreadfully confusing!"
    - Alice is right, there MUST be jam today. Language is only what we use to describe.
      While it is how we dictate in reality it does not dictate our reality!
      - The past, present, and future exist simultaneously for them to exist at all.
        - If we are completely describing our system context
          - Each angle in our Trinity folds into the others if the others aren't there
            - In describing it at all cause the cascading effect
              - For there to be a tomorrow, there must be a today
                - Cross ref: between the frames
                - It's all just deltas
                  - This is how we exploit in vol 3 attack 2

### Manifest: Alice Log TODOs

- Upstream
  - Recurse with no overlay or orchestrator
- Overlay
  - Populate JSON Source with a record with a repo name and records
    - [`alice shouldi contribute`](https://github.com/intel/dffml/tree/alice/entities/alice/#contribute)
    - Overlay
      - `-sources dev=json -source-dev-filename .tools/open-architecture/innersource/repos.json -source-dev-readwrite -source-dev-allowempty`
      - Dataflow to read project name and associated repos from config file
        - Upstream
          - https://github.com/intel/dffml/blob/alice/entities/alice/CONTRIBUTING.rst#writing-operations
        - Overlay
          - Alice, please write an operation to read `repos` top level key similarly to how `name` was read.
      - Repo with `myconfig` in it compliant to allowlisted operation implementations which read `repos` and `name` keys
  - Repos As Given By JSON Source
    - `-sources dev=json -source-dev-filename .tools/open-architecture/innersource/repos.json`
  - Select project Repo IDs using `name` feature
    - https://unix.stackexchange.com/questions/501577/if-else-in-jq-is-not-giving-expected-output
- Orchestrator
  - gitpod
- Notes for Downstreams
  - Use of `~` (User home directory) should be switched to a tempdir

```console
$ python -m dffml list records -log debug -sources dev=json -source-dev-filename .tools/open-architecture/innersource/repos.json | tee ~/.projects.$(date -Iseconds).json
$ cat $(ls ~/.projects* | tail -n 1) | jq -r '.[] | select(.features.name == "My Custom Name") | .' | python -c "import sys, pathlib, json, yaml; print(yaml.dump(json.load(sys.stdin)))"
```

```yaml
extra: {}
features:
  name: My Custom Name
  repos:
  - 0
key: otherkey
```

```console
$ (for repo_id in  $(ls ~/.projects* | tail -n 1) | jq -r '.[] | select(.features.name == "My Custom Name") | .features.repos[]'); do export repo_url=$(gh api --jq '.clone_url' "/repositories/${repo_id}"); echo "$repo_id $repo_url" && gh issue list --search "Recommended Community Standard:" -R "${repo_url}"; done) 2>&1 | tee .gh.issue.list.$(date -Iseconds).txt
```

### WebUI Discussion

- Within WASM
  - Pass manifest
    - IPVM
    - DataFlow
    - #1300
    - HASH validation (similar to JSON schema?)? of stringified form for trampoline encoding (upstream : Input DID/CID)
    - https://pyodide.org/en/stable/usage/api/js-api.html?highlight=globals#pyodide.unpackArchive
    - https://pyodide.org/en/stable/usage/api/js-api.html?highlight=globals#pyodide.globals
    - https://pyodide.org/en/stable/usage/api/js-api.html?highlight=globals#pyodide.loadPackagesFromImports

```html
<!DOCTYPE html>
<html>
  <head>
      <script src="https://cdn.jsdelivr.net/pyodide/v0.21.3/full/pyodide.js"></script>
  </head>
  <body>
    <script type="text/javascript">
      async function main(){
        let pyodide = await loadPyodide();
        console.log(pyodide.runPython("1 + 2"));
      }
      main();
    </script>
  </body>
</html>
```

```javascript
// hello_python.js
const { loadPyodide } = require("pyodide");

async function hello_python() {
  let pyodide = await loadPyodide();
  return pyodide.runPythonAsync("1+1");
}

hello_python().then((result) => {
  console.log("Python says that 1+1 =", result);
});
```

### Infra roll call

#### Domains

- [x] dffml.org
  - Keymakers: Saahil
- [x] chadig.com
  - Keymakers: John
- [x] nahdig.com
  - Keymakers: John

### PyCascades

- We want to present some of the core tutorial concepts, the system context
  - ... or maybe it's about Alice? ... and the system context is more techniacl deails for a deep dive
  - Obviouslly it's all about Alice, but the user faceing part ASAP (Alice ASAP), is the CLI and hopefully issue ops, etc.
- Description
  - This talk will delve into the ever deepening rabbit hole of maintenance tasks we as developers end up doing to keep our software projects as healthy as possible. We'll start with an idea, the original sin if you will, following our train of thought until we have a little application we can kick the tires on. As our project's releases start rolling we'll begin building and refining policies and actions. Alice rolls with us as we overlay context aware responses to lifecycle events such as CVEs. We'll see how Alice helps us understand and strengthen our software's security posture and overall health as our software evolves over time. When all's said and done we'll have a secure rolling release in alignment with the project's strategic principles and values, measurable, auditable, actionable. Data, Analysis, Control (DAC).
  - [image](https://user-images.githubusercontent.com/5950433/204975023-021a0e3e-4b74-460f-8f76-e7ca164af983.png)
  - [2022-11-30 22-40-59-If-You-Give](https://user-images.githubusercontent.com/5950433/205342085-74ac0d95-3ab7-4b84-bf4b-2af355cccf2c.png)

---

- TODO
  - [x] Infra roll call
  - [ ] **PYCASCADES!!!**
    - [x] Updated https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_architecting_alice/0002_shes_ariving_when.md
        - https://github.com/intel/dffml/commit/408d0ef29f60d0289fc2f7b6097faf8da9e6a8af
      - Sourced from ^
    - [x] Picture
      - [2022-11-30-profile-with-server-on-chain](https://user-images.githubusercontent.com/5950433/205323625-ddca2a42-f908-4e7b-936e-0d09d62af175.jpg)
        - > Eventually we'll build this thing. It obviously works! LMAFOOOOOOO
          - Original post on mastodon but maybe it was a little too much :P
    - [x] Bio
      - ~~Lives life with curiosity, understanding, and passion itself. Current focus is around leveraging threat model and architecture information to facilitate automated context aware decentralized gamification / continuous improvement of the security lifecycle / posture of open source projects.~~
      - Lives life with curiosity. Current focus is around leveraging threat model and architecture information to facilitate automated context aware decentralized gamification / continuous improvement of the security lifecycle / posture of open source projects.
  - [ ] Search for fourth eye
    - https://search.brave.com/search?q=the+fourth+eye&source=web
    - http://apocalypsefatigue.org/dispensary/2018/2/11/the-fourth-eye
      - Wow
    - http://apocalypsefatigue.org
    - http://apocalypsefatigue.org/score
      - > Themes will be expanded, and techniques will be shared. We will beat the Game together.
      - Shit, that email I wrote earlier and didn't send...
  - [ ] Quote above pyjs wasm snippits
  - [ ] Alice Please Contribute Issue Ops
  - [ ] DevCloud GitHub Actions based melange OS DecentrAlice CI for DFFML for maintainer only execution (managing a secondary deployment, should be runnable same workflow on public or DevCloud based runners.
    - [ ] https://github.com/chainguard-dev/crow-registry
      - [ ] Local / open source / deployable equivalent no lock in v8workers runtime?
      - [ ] Authenticated push via OIDC -> Notary -> SCITT Receipt patterns
      - [ ] Cross-repo blob mounting
      - [ ] OCI conformance
        - https://github.com/opencontainers/distribution-spec/blob/main/spec.md
        - https://github.com/oras-project/oras-py
          - Upload metrics collected data via add hock package creation
          - https://github.com/intel/dffml/blob/1513484a4bf829b86675dfb654408674495687d3/dffml/operation/stackstorm.py#L306-L368
      - [ ] Proxy to PyPi registry format
      - [ ] Cross SCITT https://scitt.io/distributing-with-oci-scitt.html with NPM RFC and mention in OpenSSF Metrics Use Case https://github.com/npm/rfcs/pull/626/files?short_path=9e1f9e7#diff-9e1f9e7b9ebe7e135d084916f727db5183eddd9bf2d9be73ca45444b6d74bfc9 to produce reference env docs for OpenSSF and SCITT on how DFFML does inventory and manifests
        - #1207
        - #1273
        - Use to update CI in #1401
          - Once CI works rebase main then rebase into main then we'll be rolling (slowly, but at least we'll have all systems green for the first time in a long time and be able to start acctually increasing acceleration with our basic build flow established. Need to do stream of consciousness seen bellow first before the downstream validation / metric data as package / puload / downstream flow trigger stuff works (websub + OA -> event / effect / downstream CI/CD triggered via VEX).
    - [ ] Deploy Stream of Consciousness either via similar worker pattern as inventory or originally planned methods mentioned here
      - [ ] SSI Service or DWN
        - [ ] SCITT yin yang style integration (dffml / console test ideal)
      - [ ] VEX / SBOM based downstream validation
      - [ ] Rebuild chains `FROM`
        - [ ] `dffml-service-http`
        - [ ] `dffml[models|...|all]`
  - [ ] Detect 12 factor app alignment
  - [ ] Move Vol 3 attack 2 draft from discussion thread into tutorial location
    - Update with jam today, we are exploiting the abitrage between those deltas on the data
    - Our mitigation here is our bus factor in train of though threat model risk analysis lcality aware caching hit raito trade off with cache restoration response time (bus factor loss, acceptable documentation loss to maintain acceleration within train of thought)
      - As mentioned in Alice thread, we always have the upper hand on thought arbitrage due to locality, when working in ad-hoc groups furthering state of art in trains of thought we use the AI/ML equivilant of speaker (think waves, patterns) syncing. We do this via communicating models and stragatic plans across EDEN nodes (Alice Instances), best practices, measurements, processes for data tranformation, trust assement within context etc, this is why we need the Open Architecture/DataFlow/IPVM style execution, it's sandboxed.
      - The same techniques we are using to ensure all of our buddies are up to speed and not working in the wrong direction are the things we are giong ot try to predict as an atacker and look for what data we can introduce into injection via introspection of target trust chains to preform subconsous attacks via train of thought graffiti. We abitrarage them first effectivly so we can understand how their data minging feature data (bottom of iceburg) all the way up to hyper parameters (strategic plans) effect their oracle trust evaluation likely paths.
        - We leverage this information / predictions to attempt to move their trusted oracles to source data or proceses from supply chain vectors we have the ability to influence by getting our data in there in a way that will effecct their model (example: bunch of misslabeled VEX).
        - This is closely related / dependent on our `A Shell for a Ghost` future work train of thought detection so as to help developers stay on track and not working down unproductive trains of thought (value stream mapping, system context as todo / github issue, see `Manifest: Alice Log TODOs` above, branch / shell exit / fuzzy find output / snapshot dynamic filesystem, system context / dataflow / cache based deltas)
          - Mention Alice as a tool to help manage ADHD
            - Alice, please help with ADHD
            - Alice, please help us finish this without reaching L_burnout=5 DEFCON=1
              - Alright, back down the rabbit hole to Wonderland and get in the zone.
              - God's speed. Good luck.
              - Thanks dude, and thank you Alice.
              - Wow. Wow. Wow.
                - apocalypsefatigue.org root score indeed! privsec succeeded we've found the other sudoers.
                - Thanks again Alice :heart:
                - Yes GitHub suggestion, Distributed Orchestration what we are hoping to achive here hopefully these folks can program or we just cordinate maybe cross ref the book contents to the code!!! Yes yes, thanks for technically buggng out and suggesting this issue. Let's convert this to something about mapping workstreams. Okay peace out, wild day.
                  - #772 
  - [x] WebUI discussion
    - #33
    - #169
    - #363
      - First steps: https://pyodide.org
      - Next Steps: #1207
  - [ ] https://github.com/intel/cve-bin-tool/pull/2384
    - https://www.cisa.gov/sites/default/files/publications/VEX_Use_Cases_Aprill2022.pdf
    - Back off to only test the one apiv2 that was working with the mock server
      - Log other tests as todos and com back later or hand off to other cve bin tool community members.
  - [ ] Mention potentially aligned (if aligned work)
    - https://community.apan.org/wg/tradoc-g2/mad-scientist/m/back-to-the-future-using-history-to-forecast/427122
    - "Futurist Amy Webb on why scenario planning is key to creating a more resilient world." Read on the [World Economic Forum.](https://www.weforum.org/agenda/2022/01/futurist-amy-webb-on-the-importance-of-scenario-planning/)
      - > It’s about flexibility. Most people and organizations are very inflexible in how they think about the future. In fact, it’s difficult to imagine yourself in the future, and there are neurological reasons for that. Our brains are designed to deal with immediate problems, not future ones. That plus the pace of technology improvement is becoming so fast that we’re increasingly focused on the now. Collectively, we are learning to be “nowists,” not futurists.
       >
       > Here’s the problem with a “nowist” mentality: when faced with uncertainty, we become inflexible. We revert to historical patterns, we stick to a predetermined plan, or we simply refuse to adopt a new mental model.
       - Hence our "Predict the future with Us" chapter, which should be near the wardly map stuff
         - Stop getting distracted

---

Okay I think we kill enough birds with the same stones to get this done.