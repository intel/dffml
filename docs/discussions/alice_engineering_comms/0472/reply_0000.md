## 2023-12-05 @pdxjohnny Engineering Logs

- The following is a snapshot of #1401 pull request body at time of rebase

---

- Alice is Here! It’s the 2nd Party and everyone is invited 💃🥳. Alice is both the nickname for the Open Architecture, the methodology of description of any system architecture, as well as the entity defined using that description of architecture. She is *the entity and the architecture.*
- https://github.com/intel/dffml/discussions/1406?sort=new
  - Get involved by commenting in the discussion thread!
- What to expect
  - Alice ready for contribution
    - Completed: 2022-07-29
    - [Coach Alice Our Open Source Guide](https://github.com/intel/dffml/blob/main/docs/tutorials/rolling_alice/0001_coach_alice/0002_our_open_source_guide.md)
    - [General Alice Contribution Docs](https://github.com/intel/dffml/blob/main/entities/alice/CONTRIBUTING.rst#tutorials)
  - We'll be rebasing this branch into main once the CI for 2ndparty plugin support passes (see closed PR with ADR, only closed because of branch rewrite to remove images, will be reopened asap).
    - ETA: 2023-06-01
  - We'll then rewrite history again, splitting the plugins out into their respective 2ndparty maintenance locations (dffml or builtree org or possibly other option on stay with 2ndparty within intel org, weâ€™ll see how it goes pending governance review).
    - ETA: 2023-11-30
  - Finally, weâ€™ll flip the switch to our web5 world, where git is only used as a proxy for commit data encoded via DIDs. We will then have ourstory, from then on everything will be Alice. Alice will be the methodology by which we interpret those nodes, DIDs in the web5 case. Alice will also exist as the entity whose execution is based on the same methodology used for definition of the graph.
    - ETA: 2024-11-30
- Code
  - Alice
    - https://github.com/intel/dffml/tree/main/entities/alice
- Documentation
  - [Status Updates](https://www.youtube.com/playlist?list=PLtzAOVTpO2jZltVwl3dSEeQllKWZ0YU39)
  - Engineering Logs
    - [Progress Reports](https://www.youtube.com/playlist?list=PLtzAOVTpO2jYt71umwc-ze6OmwwCIMnLw)
    - https://github.com/intel/dffml/discussions/1406
    - [Volume 0: Architecting Alice](https://www.youtube.com/playlist?list=PLtzAOVTpO2jaHsS4o-sDzDyHEug-1KRbK)
    - [Volume 1: Coach Alice](https://www.youtube.com/playlist?list=PLtzAOVTpO2jaXSPFcTOUeg3LKV5oMhKR7)
  - Contributing
    - [Google Doc: Alice Community any and all Miscellaneous Thoughts](https://docs.google.com/document/d/1-98h1NWagbQbRYEkRHA7Kb-TuanmackGwtcvKIMqB0c/edit)
      - For those less comfortable with GitHub.
    - [Writing Alice Overlays](https://github.com/intel/dffml/blob/main/entities/alice/CONTRIBUTING.rst)
  - Tutorials
    - [ ] [Rolling Alice](https://github.com/intel/dffml/tree/main/docs/tutorials/rolling_alice)
      - [ ] [Forward](https://github.com/intel/dffml/blob/main/docs/tutorials/rolling_alice/0000_forward.md)
      - [ ] [Preface](https://github.com/intel/dffml/blob/main/docs/tutorials/rolling_alice/0000_preface.md)
      - [ ] [Easter Eggs](https://github.com/intel/dffml/blob/main/docs/tutorials/rolling_alice/0000_easter_eggs.md)
      - [ ] [Architecting Alice: Introduction and Context](https://github.com/intel/dffml/tree/main/docs/tutorials/rolling_alice/0000_architecting_alice)
        - [x] [Peace at Last](https://github.com/intel/dffml/blob/main/docs/tutorials/rolling_alice/0000_architecting_alice/0001_peace_at_last.md)
        - [ ] [Sheâ€™s Arriving When?](https://github.com/intel/dffml/blob/main/docs/tutorials/rolling_alice/0000_architecting_alice/0002_shes_ariving_when.md)
        - [ ] [A Shell for a Ghost](https://github.com/intel/dffml/blob/main/docs/tutorials/rolling_alice/0000_architecting_alice/0003_a_shell_for_a_ghost.md)
        - [ ] [Writing the Wave](https://github.com/intel/dffml/blob/main/docs/tutorials/rolling_alice/0000_architecting_alice/0004_writing_the_wave.md)
        - [ ] [Stream of Consciousness](https://github.com/intel/dffml/blob/main/docs/tutorials/rolling_alice/0000_architecting_alice/0005_stream_of_consciousness.md)
        - [ ] [OS DecentrAlice](https://github.com/intel/dffml/blob/main/docs/tutorials/rolling_alice/0000_architecting_alice/0006_os_decentralice.md)
        - [ ] [An Image](https://github.com/intel/dffml/blob/main/docs/tutorials/rolling_alice/0000_architecting_alice/0007_an_image.md)
      - [ ] [Coach Alice](https://github.com/intel/dffml/tree/main/docs/tutorials/rolling_alice/0001_coach_alice)
        - [x] [Introduction](https://github.com/intel/dffml/blob/main/docs/tutorials/rolling_alice/0001_coach_alice/0000_introduction.md)
        - [ ] [Down the Dependency Rabbit-Hole Again](https://github.com/intel/dffml/blob/main/docs/tutorials/rolling_alice/0001_coach_alice/0001_down_the_dependency_rabbit_hole_again.md)
        - [x] [Our Open Source Guide](https://github.com/intel/dffml/blob/main/docs/tutorials/rolling_alice/0001_coach_alice/0002_our_open_source_guide.md)
        - [ ] [Strategic Principles as Game Plan](https://github.com/intel/dffml/blob/main/docs/tutorials/rolling_alice/0001_coach_alice/0003_strategic_principles_as_game_plan.md)
        - [ ] [You are what you EAT!](https://github.com/intel/dffml/blob/main/docs/tutorials/rolling_alice/0001_coach_alice/0004_you_are_what_you_EAT.md)
        - [ ] [In the Lab](https://github.com/intel/dffml/blob/main/docs/tutorials/rolling_alice/0001_coach_alice/0004_in_the_lab.md)
        - [ ] [An Open Book](https://github.com/intel/dffml/blob/main/docs/tutorials/rolling_alice/0001_coach_alice/0005_ask_alice.md)
        - [ ] [Cartographer Extraordinaire](https://github.com/intel/dffml/blob/main/docs/tutorials/rolling_alice/0001_coach_alice/0007_cartographer_extraordinaire.md)
  - ADRs
    - [Manifest](https://github.com/intel/dffml/tree/main/docs/arch/0008-Manifest.md)
    - [Open Architecture](https://github.com/intel/dffml/tree/main/docs/arch/0009-Open-Architecture.rst)
    - [DID + HSM Supply Chain Security Mitigation Option](https://github.com/intel/dffml/tree/main/docs/arch/0007-A-GitHub-Public-Bey-and-TPM-Based-Supply-Chain-Security-Mitigation-Option.rst)
  - Work which lives with other groups
    - [SCITT OpenSSF Use Case](https://github.com/pdxjohnny/use-cases/blob/openssf_metrics/openssf_metrics.md)
      - This serves as security for our stream of consciousness.
    - https://github.com/w3c/cogai/pull/47
- Tagged RFCs
  - RFCv3: https://github.com/intel/dffml/tree/516d9276cd8795e8bb188fadbea10e801a4cf745/docs/tutorials/rolling_alice
  - RFCv2: https://github.com/intel/dffml/tree/2331ba7a7e433d8fcb6698ada92be48fdc225c3e/docs/tutorials/rolling_alice
  - RFCv1.1:  https://github.com/intel/dffml/tree/69df6036c25f61c31af21b1db9b7f14327147a9e/docs/tutorials/rolling_alice
  - RFCv1: https://github.com/intel/dffml/tree/291cfbe5153414932afe446aa4f6c2e298069914/docs/tutorials/rolling_alice
    - Began by exploring how we should write clean dataflow docs in https://github.com/intel/dffml/issues/1279
    - Converted to discussion in https://github.com/intel/dffml/discussions/1369
    - Issue converted to discussion converted to files within https://github.com/intel/dffml/blob/main/docs/arch/alice/discussion/
    - Pulled out existing ADRs and tutorials in their current states into
      - Tutorials
        - [Rolling Alice](https://github.com/intel/dffml/tree/main/docs/tutorials/rolling_alice)
      - ADRs
        - [Manifest](https://github.com/intel/dffml/tree/main/docs/arch/0008-Manifest.md)
        - [Open Architecture](https://github.com/intel/dffml/tree/main/docs/arch/0009-Open-Architecture.rst)
        - [DID + HSM Supply Chain Security Mitigation Option](https://github.com/intel/dffml/tree/main/docs/arch/0007-A-GitHub-Public-Bey-and-TPM-Based-Supply-Chain-Security-Mitigation-Option.rst)
    - Cross linked tutorials with their usage examples within README within alice entity directory https://github.com/intel/dffml/tree/main/entities/alice
- TODO (extra todos: https://github.com/intel/dffml/pull/1401#issuecomment-1168023959)
  - [x] Clean up tutorial docs that currently exist
    - [x] Find home for them in tree
      - https://github.com/intel/dffml/blob/main/docs/tutorials/rolling_alice/
    - [x] Tentative chapter name for Question and Answering model
      - Volume 1: Coach Alice: Chapter 5: Question Everything
        - https://github.com/programmer290399/IT-710-Project-Video-QnA-System
  - [ ] DataFlow.export should include $schema as should all .export() methods.
    - [ ] Later for operations the schema is the schema for the associated manifest.
  - [x] Split overlays into separate file locations
    - [x] Update Alice contributing docs with new paths instead of AliceGitRepo omport from alice.cli
  - [ ] Docs build with `alice` branch if working
  - [ ] Run auto formatter on every commit in alice branch
  - [ ] Cloud development environment options
    - Public
      - [ ] GitPod
        - https://gitpod.io/#github.com/intel/dffml/tree/main
        - TODO
          - `mv dffml/operations/python.py operations/innersource/dffml_operations_innersource/python_ast.py`
          - Add Alice CONTRIBUTING setup to the `.gitpod.yml` auto start setup
            - `code tutorial.ipynb` when done
    - Self-Hosted
      - [ ] Coder
        - https://coder.com/docs/coder-oss/latest/install
  - [x] Alice contributing documentation
    - https://github.com/intel/dffml/blob/main/entities/alice/CONTRIBUTING.rst
      - [x] How to extend recommended community standards command with overlays
        - Basic tutorial where we grab the name from a configuration file
      - [ ] Show me a security overlay.
        - Write section of our open source guide tutorial where we implement the SECURITY.md overlay
        - Latwr go back and write how we implemented the base flow and the initial set of overlays, and the readme overlay.
          - We can prototype the use of commit messages as docs and commit the whole file when we move it with docs for that overlay, rST in commit message. Later explore log of file to changelog in rST to sphinx docs.
          - Link up with herstory to ipynb creation and shell command saving. Auto generate commit messages (docs) based on herstorical shell commands ran (or if in vscode debug buttons or run buttons executed) with output. Diff system context herstory state with link in chain at last clean tree. Run timeline resolution if dirty tree for set of commits (multiple git add runs). First we automate writing the docs, then we automate reading.
      - [ ] How to write new commands
      - [ ] Non CLI interfaces
  - [ ] Physical party - TBD probably 2029, 2030
  - [ ] Commenting in issue while debugging, this is an overlay to herstory collection
  - [ ] Get tbDEX up and running for backing storage
    - [ ] Write an operation that inserts data into tbDEX format, either via API or flat file duplication of formatting via libraries like the Python peerdid library.
  - [ ] Use @programmer290399's QA model to implement `alice ask` which queries all our docs, logs, notes, issues, etc.
    - https://programmer290399.github.io/pyqna/usage.html
- Alice enables granular identification and application of static or dynamic policy.
  - She does this through context aware overlays whose application process to upstream may be dynamic, even in part end user (attacker) flows, which can be executed or synthesized within an appropriate (optionally adaptive, we do dynamic and static and we understand time across so we can come re synthesize in your codebase on trigger) sandbox

---

- Next step is setup sync of testing CI workflows across 2nd party repos
  - We'll send events to the https://scitt.unstable.chadig.com demo instance
    - https://github.com/pdxjohnny/scitt-api-emulator/tree/demo-instance
    - https://github.com/pdxjohnny/scitt-api-emulator/tree/bf74838c3444995196ad8c04c3d25cf1db639108

```python
import asyncio
import aiohttp
import json

# Your personal access token
TOKEN = "your_github_access_token"

# The GraphQL query template
QUERY_TEMPLATE = """
query($repo_name: String!, $owner: String!, $path: String!) {
  repository(name: $repo_name, owner: $owner) {
    pullRequests(first: 10, states: OPEN) {
      nodes {
        title
        files(first: 10) {
          nodes {
            path
            if (path == $path)
            {
              pullRequest {
                url
              }
            }
          }
        }
      }
    }
  }
}
"""

# Replace with your GitHub repositories and the file you want to check
REPOS = [("owner1", "repo1"), ("owner2", "repo2")]
FILE_PATH = "path/to/your/file.txt"

async def fetch_prs(session, owner, repo, file_path):
    payload = {
        "query": QUERY_TEMPLATE,
        "variables": {
            "owner": owner,
            "repo_name": repo,
            "path": file_path,
        },
    }
    headers = {
        "Authorization": f"token {TOKEN}",
        "Content-Type": "application/json",
    }

    async with session.post('https://api.github.com/graphql', json=payload, headers=headers) as response:
        prs = await response.json()
        return prs


async def main(repos, file_path):
    async with aiohttp.ClientSession() as session:
        async with asyncio.TaskGroup() as tg:
            for owner, repo in repos:
                tg.create_task(fetch_prs(session, owner, repo, file_path))

        results = [t.result() for t in tg.tasks if t.done()]

    return results

# Running the main coroutine
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    pr_data = loop.run_until_complete(main(REPOS, FILE_PATH))
    # Process your PR data as needed
    print(json.dumps(pr_data, indent=2))
```

- https://socialweb.coop/blog/
- TODO
  - [x] Rebase #1401 into main
  - [x] https://github-webhook-notary.scitt.alice.chadig.com/github-webhook-notary/
    - [ ] Update unstable demo instance
  - [ ] POC 2nd party repo file updates
  - [ ] Get on SCITT slack
  - [x] Respond to Ben with Actor URIs once we've got the notarizing proxy fully hooked up
    - [ ] Disable wipe of sqlite DB
    - [ ] 1:30-2 1:1 with Ben