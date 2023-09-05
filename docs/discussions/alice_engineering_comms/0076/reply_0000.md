## 2022-11-04 @pdxjohnny Engineering Logs

- Issue Ops as a way for people to request Alice pull requests, contributions, interaction, etc.
  - https://github.com/valet-customers/issue-ops/blob/6a5e64188ae79dfd11613f5f9bdc75f7b769812b/.github/workflows/issue_ops.yml
  - https://github.com/valet-customers/issue-ops/blob/6a5e64188ae79dfd11613f5f9bdc75f7b769812b/.github/ISSUE_TEMPLATE/gitlab_ci.md
- How do we communicate and document when there is new data available or we plan to make new data available.
- How do we uqyer and correlate across sources?
- VEX (JSON-LD?)
  - Statuses
    - Investigating
    - Vulnerable
    - Used but not vulnerable
    - This version is vuln (to vuln or dep vuln) but we have another one that's not effected
  - We will need to establish chains of trust on top of VDR / VEX issuance
  - https://cyclonedx.org/capabilities/vdr/#bom-with-embedded-vdr
  - https://www.nist.gov/itl/executive-order-14028-improving-nations-cybersecurity/software-security-supply-chains-software-1
  - https://cyclonedx.org/capabilities/vex/
  - https://energycentral.com/c/pip/what-nist-sbom-vulnerability-disclosure-report-vdr
  - https://github.com/CycloneDX/bom-examples/blob/master/SaaSBOM/apigateway-microservices-datastores/bom.json
- InnerSource
  - https://innersourcecommons.org/learn/patterns/
  - https://github.com/InnerSourceCommons/InnerSourcePatterns
  - https://www.youtube.com/watch?v=RjBpZKsAQN0
    - A RedMonk Conversation: IBM's Inner Source transformation, scaling a DevOps culture change.
- GitHub Actions
  - https://docs.github.com/en/actions/using-jobs/using-concurrency#example-only-cancel-in-progress-jobs-or-runs-for-the-current-workflow
  - https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#concurrency
- https://code-as-policies.github.io/
  - Need to look into this more
  - https://colab.research.google.com/drive/1V9GU70GQN-Km4qsxYqvR-c0Sgzod19-j
  - https://ai.googleblog.com/2022/11/robots-that-write-their-own-code.html
  - https://web1.eng.famu.fsu.edu/~mpf/research.htm
  - > Central to this approach is hierarchical code generation, which prompts language models to recursively define new functions, accumulate their own libraries over time, and self-architect a dynamic codebase.
    - Yup
- https://twitter.com/MikePFrank/status/1588539750423547905
  - Reversible Computing
    - Essentially what we get when we cache our flows plus all our equilibrium reaching time travel stuff (synchronization of system contexts across disparate roots, aka cherry picking patches and A/B validation of results until we reach desired state)
    - https://en.wikipedia.org/wiki/Reversible_computing
- http://hiis.isti.cnr.it/serenoa/project-fact-sheet.html
  - Some similar principles to ours
  - > - New concepts, languages, (intelligent) runtimes and tools are needed to support multi-dimensional context-aware adaptation of SFEs. h ese artefacts will enable SFE engineers to concentrate on the functionality rather than on the implementation details concerning the adaptation to the multiple dimensions of the context of use.
    > - Keeping Humans in the Loop. h is principle is twofold. On the one hand, end users should be able to provide feedback or even guide the adaptation process according to their preferences or previous experiences with the system. On the other hand, authors, developers and engineers should be able to guide the adaptation process according to their experience and domain knowledge.
    > - Open Adaptiveness. A system is open adaptive “if new adaptation plans can be introduced during runtime”. - Adaptation in ubiquitous computing environments (such as in ambient spaces) is also necessary in order to deal with multiple devices, interaction resources and modalities.
    > - Covering the full adaptation lifecycle to support a full adaptation life-cycle that will result into feedback loops (coming from end users) in order to inform any future adaptation

```python
async def gh_issue_create_if_file_not_present(
    repo_url: str,
    file_present: bool,
    title: str,
    body: str,
    logger: logging.Logger,
) -> Dict[str, str]:
    if file_present:
        return
    return {
        "issue_url": await gh_issue_create(
            repo_url,
            title,
            body,
            logger=logger,
        )
    }


"""
def make_gh_issue_create_opimp_for_file(
    filename: str,
    file_present_definition,
    default_title: str,
    body: str,
):
    IssueTitle = NewType(filename + "IssueTitle", str)
    IssueBody = NewType(filename + "IssueBody", str)
    IssueURL = NewType(filename + "IssueURL", str)

    # TODO,
    # NOTE dffml.op requires name set in overlay classes for now

    return new_types, opimp
"""


# : dffml_operations_innersource.operations.FileReadmePresent
class AlicePleaseLogTodosDataFlowRecommendedCommnuityStandardsGitHubIssues:
    @dffml.op(
        inputs={
            "repo": dffml_feature_git.feature.definitions.git_repository_checked_out,
            "file_present": dffml_operations_innersource.operations.FileSupportPresent,
            "title": SupportIssueTitle,
            "body": SupportIssueBody,
        },
        outputs={
            "issue_url": NewType("SupportIssueURL", str),
        },
    )
    async def gh_issue_create_support(
        repo: dffml_feature_git.feature.definitions.git_repository_checked_out.spec,
        file_present: bool,
        title: str,
        body: str,
    ) -> Dict[str, str]:
        return await gh_issue_create_if_file_not_present(
            repo.URL,
            file_present,
            title,
            body,
            logger=self.logger,
        )


"""
cls = AlicePleaseLogTodosDataFlowRecommendedCommnuityStandardsGitHubIssues
for new_types, opimp in itertools.starmap(
    make_gh_issue_create_opimp_for_file,
    [
        ("Support", dffml_operations_innersource.operations.FileSupportPresent),
        ("Contributing", dffml_operations_innersource.operations.FileContributingPresent),
        ("CodeOfConduct", dffml_operations_innersource.operations.FileCodeOfConductPresent),
        ("Security", dffml_operations_innersource.operations.FileSecurityPresent),
    ],
):
    setattr(cls, opimp.op.name, )
    for new_type in new_types:
        print(new_type, new_type.__dict__)
"""
```

- alice: please: log: todos: recommended community standard: support: github issue: Allow for title and body override
  - 67d79ede39629f3b117be0d9f2b5058f88b4efcb
- e2ed7faaa alice: please: log: todos: recommended community standard: code of conduct: github issue: Log issue if file not found
- 8b0df460a alice: please: log: todos: recommended community standard: contributing: github issue: Log issue if file not found
- dbb946649 alice: please: log: todos: recommended community standard: security: github issue: Log issue if file not found
- 59d3052f9 alice: please: log: todos: recommended community standard: Cleanup comments
- 5dbadaf36 operations: innersource: Check for README community health file
- d867a9cda  alice: please: log: todos: recommended community standard: readme: github issue: Log issue if file not found

![image](https://user-images.githubusercontent.com/5950433/200097693-4207fe5c-6d0d-4bfb-8d75-d57bd5768616.png)

![image](https://user-images.githubusercontent.com/5950433/200098670-1085a185-71af-4193-b5ca-5740d42c952d.png)

- Ran the three most recent Alice commands to confirm everything is still working
  - `alice shouldi contribute`
  - `alice please log todos`
  - `alice please contribute recommended community standards`

```console
$ alice -log debug shouldi contribute -keys https://github.com/pdxjohnny/testaaa
$ alice please log todos -log debug -keys https://github.com/pdxjohnny/testaaa
$ alice please contribute -repos https://github.com/pdxjohnny/testaaa -log debug -- recommended community standards
```

- 7980fc0c7 util: cli: cmd: Add DFFMLCLICMD NewType for use in data flows
- 6d0ce54e1 cli: dataflow: run: records: Allow for passing CLI CMD instance to data flow as input
- 0356b97a9 alice: cli: please: contribute: recommended community standards: Use CLI CMD type from dffml
- 3e8b161a2 alice: cli: please: log: todos: Use CLI CMD type from dffml
- 7c7dd8f7c alice: cli: please: log: todos: Base off dffml dataflow run records
- 1d4d6b2f8 alice: cli: please: log: todos: Explictly pass directory when finding last repo commit
- TODO
  - [ ] SaaSBOM etc. overlays for dataflows for `THREATS.md` analysis
    - https://github.com/CycloneDX/bom-examples/tree/6990885/SaaSBOM/apigateway-microservices-datastores
  - [ ] Find a cleaner way to do same operation reused with different definitions (and defaults)