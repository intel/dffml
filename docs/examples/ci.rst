Continuous Integration
======================

In this example we're going to build a continuous integration system.

Problem Statement
-----------------

GitHub Actions is great on a per repo basis. Sometimes you have the same CI job
that you'd like to run on multiple repos, only changing the config per repo.

One way you could do that is by adding the same workflow file to each repo.
However, this means you have to keep those workflow files in sync across repos
when the workflow is updated.

This example will cover building a CI system where workflows are centrally
managed. This eliminates variation between repo workflows and enables
organizational consistency.

Plan
----

Let's plan out how our CI process should work.

We know we're building a centralized CI service, so we want a main CI repo.
We'll call each other repo a Repo Under Test (RUT). We're assuming there are
``N`` RUTs, in the below description we describe one instance, since they are
all the same fundamentally.

- Central CI repo

  - Has access to compute to run each jobs for each RUT

    - In this example we'll assume compute is being provided by Kubernetes.
      You could host on different compute by writing an ``Orchestrator`` to
      interact with your platform / infrastructure as a service of choice.
      **TODO** Tutorial on writing an ``Orchestrator``
      https://github.com/intel/dffml/issues/1250

  - Has access to secrets

    - Secret management must allow for pre RUT secrets and globally applicable
      secrets to be accessed by the central CI repo.

  - Contains CI jobs to run

    - These will be in the form of DataFlows

  - Contains mappings of which CI jobs to run on which RUTs

    - These will be in the form of DataFlows

- Repos Under Test (RUTs)

  - Contain code

  - Contain jobs that are specific to just that repo

.. literalinclude:: /../examples/innersource/swportal/operations/gh.py
    :test:

.. code-block:: python
    :test:
    :filepath: gh.py

    import os

    import dffml
    import github


    @dffml.op(
        inputs={
            "url": dffml.Definition(name="github.repo.url", primitive="string"),
        },
        outputs={
            "owner": dffml.Definition(
                name="github.org.owner_name", primitive="string"
            ),
            "project": dffml.Definition(
                name="github.repo.project_name", primitive="string"
            ),
        },
    )
    def github_split_owner_project(url):
        """
        Parses the owner and project name out of a GitHub URL

        Examples
        --------

        >>> github_split_owner_project("https://github.com/intel/dffml")
        ('intel', 'dffml')
        """
        return dict(
            zip(
                ("owner", "project"),
                tuple("/".join(url.split("/")[-2:]).split("/")),
            )
        )


    @dffml.config
    class GitHubGetRepoConfig:
        # TODO Set field as secret once dffml has support for secret fields
        token: str = dffml.field(
            "GitHub Personal Authentication Token",
            default=os.environ.get("GITHUB_TOKEN", None),
        )

    make_config_inspect(github.Commit.create_status)

    @dffml.op(
        inputs={"repo": github_get_repo.op.outputs["repo"],},
        outputs={
            "raw_repo": dffml.Definition(
                name="PyGithub.Repository.Raw", primitive="object"
            ),
        },
    )
    def github_repo_create_status(repo, sha, status):
        # sha -> commit on which the status check will be created
        # For example, for a webhook payload
        # sha = data["pull_request"]["head"]["sha"]
        repo.get_commit(sha=sha).create_status(
            state="pending",
            target_url="https://FooCI.com",
            description="FooCI is building",
            context="ci/FooCI"
        )

    @dffml.op(
        inputs={
            "org": github_split_owner_project.op.outputs["owner"],
            "project": github_split_owner_project.op.outputs["project"],
        },
        outputs={
            "repo": dffml.Definition(
                name="PyGithub.Repository", primitive="object",
            ),
        },
        config_cls=GitHubGetRepoConfig,
    )
    def github_get_repo(self, org, project):
        # Instantiate a GitHub API object
        g = github.Github(self.config.token)
        # Make the request for the repo
        return {"repo": g.get_repo(f"{org}/{project}")}


    @dffml.op(
        inputs={"repo": github_get_repo.op.outputs["repo"],},
        outputs={
            "raw_repo": dffml.Definition(
                name="PyGithub.Repository.Raw", primitive="object"
            ),
        },
    )
    def github_repo_raw(repo):
        return {"raw_repo": repo._rawData}

.. code-block:: python

    # If this script is run via `python gh.py intel dffml`, it will print out the
    # repo data using the pprint module.
    if __name__ == "__main__":
        import sys
        import types
        import pprint

        pprint.pprint(
            github_repo_raw(
                github_get_repo(
                    types.SimpleNamespace(config=GitHubGetRepoConfig()),
                    sys.argv[-2],
                    sys.argv[-1],
                )["repo"]
            )
        )
