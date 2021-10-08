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
