import os
import copy
import shutil
import asyncio
import tempfile
import contextlib
import subprocess
import asyncio.subprocess
from datetime import datetime
from typing import Dict, List

from dateutil.relativedelta import relativedelta

from dffml.df.types import Stage
from dffml.df.base import op
from dffml.base import config, field
from dffml.util.subprocess import Subprocess, run_command_events, run_command

from .definitions import *

from dffml_feature_git.util.proc import check_output, create, stop

from .log import LOGGER

if sys.platform == "win32":  # pragma: no cov
    asyncio.set_event_loop(asyncio.ProactorEventLoop())

TIME_FORMAT_MINTUE_RESOLUTION = "%Y-%m-%d %H:%M"


async def exec_with_logging_reader(label, reader):
    while True:
        line = await reader.readline()
        if not line:
            break
        LOGGER.debug("%s: %r", label, line)


async def exec_with_logging(*args):
    label = " ".join(args)
    LOGGER.debug("%s", label)

    proc = await asyncio.subprocess.create_subprocess_exec(
        *args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    _, _, exit_code = await asyncio.gather(
        exec_with_logging_reader(label, proc.stdout),
        exec_with_logging_reader(label, proc.stderr),
        proc.wait(),
    )

    return exit_code


@op(
    inputs={"number": quarters},
    outputs={"quarters": quarter},
    expand=["quarters"],
)
async def make_quarters(number: int):
    return {"quarters": list(range(0, number))}


@op(
    inputs={"date": quarter_start_date, "number": quarter},
    outputs={"date": date, "start_end": date_pair},
    expand=["date", "start_end"],
)
async def quarters_back_to_date(date: str, number: int):
    length, interval = number, 3
    now = datetime.strptime(date, TIME_FORMAT_MINTUE_RESOLUTION)
    return {
        "date": [
            (now - relativedelta(months=(number * 3))).strftime(
                TIME_FORMAT_MINTUE_RESOLUTION
            )
        ],
        "start_end": [
            (
                (now - relativedelta(months=(number * 3))).strftime(
                    TIME_FORMAT_MINTUE_RESOLUTION
                ),
                (now - relativedelta(months=(number * 3) + 3)).strftime(
                    TIME_FORMAT_MINTUE_RESOLUTION
                ),
            )
        ],
    }


@op(inputs={"URL": URL}, outputs={"valid": valid_git_repository_URL})
async def check_if_valid_git_repository_URL(URL: str):
    exit_code = await exec_with_logging("git", "ls-remote", URL)
    return {"valid": bool(exit_code == 0)}


@op(
    inputs={"URL": URL, "ssh_key": git_repo_ssh_key},
    outputs={"repo": git_repository},
    conditions=[valid_git_repository_URL],
)
async def clone_git_repo(self, URL: str, ssh_key: str = None):
    with tempfile.TemporaryDirectory() as ssh_key_tempdir:
        env = copy.deepcopy(os.environ)
        key = []
        if ssh_key is not None:
            ssh_key_path = pathlib.Path(ssh_key_tempdir, "id_rsa")
            ssh_key_path.write_text(ssh_key)
            env[
                "GIT_SSH_COMMAND"
            ] = "ssh -i {str(ssh_key_path.resolve()} -o UserKnownHostsFile={os.devnull} -o StrictHostKeyChecking=no"
        directory = tempfile.mkdtemp(prefix="dffml-feature-git-")

        if "GH_ACCESS_TOKEN" in os.environ and URL.startswith(
            "https://github.com"
        ):
            URL = URL.replace(
                "https://github.com",
                f"https://{os.environ['GH_ACCESS_TOKEN']}@github.com",
            )
        try:
            await run_command(
                ["git", "clone", URL, directory], env=env, logger=self.logger,
            )
        except:
            # TODO Executor shutil.rmtree
            await run_command(
                ["rm", "-rf", directory], logger=self.logger,
            )
            raise

    return {"repo": {"URL": URL, "directory": directory}}


@op(
    inputs={"repo": git_repository},
    outputs={"branch": git_branch, "remote": git_remote},
    conditions=[no_git_branch_given],
)
async def git_repo_default_branch(repo: Dict[str, str]):
    branches = (
        await check_output("git", "branch", "-r", cwd=repo.directory)
    ).split("\n")
    # If there's no branches then bail out
    if not list(filter(bool, branches)):
        return
    main = [branch for branch in branches if "->" in branch][0].split()[-1]
    # origin/HEAD -> origin/main
    # {'branch': 'main', 'remote': 'origin'}
    return dict(zip(["remote", "branch"], main.split("/", maxsplit=1)))


@op(
    inputs={"repo": git_repository, "commit": git_commit},
    outputs={"repo": git_repository_checked_out},
)
async def git_repo_checkout(repo: Dict[str, str], commit: str):
    await check_output("git", "checkout", commit, cwd=repo.directory)
    return {
        "repo": GitRepoCheckedOutSpec(
            URL=repo.URL, directory=repo.directory, commit=commit
        )
    }


@op(
    inputs={"repo": git_repository, "search": git_grep_search},
    outputs={"found": git_grep_found},
)
async def git_grep(self, repo: GitRepoSpec, search: str) -> str:
    with contextlib.suppress(RuntimeError):
        async for event, result in run_command_events(
            ["git", "grep", search],
            cwd=repo.directory,
            logger=self.logger,
            events=[Subprocess.STDOUT],
        ):
            return {"found": result.decode()}
    return {"found": ""}


@op(
    inputs={"repo": git_repository, "branch": git_branch, "date": date},
    outputs={"commit": git_commit},
)
async def git_repo_commit_from_date(
    repo: Dict[str, str], branch: str, date: str
):
    sha = (
        await check_output(
            "git",
            "rev-list",
            "-n",
            "1",
            '--before="%s"' % (date,),
            branch,
            cwd=repo.directory,
        )
    ).strip()
    if not sha:
        sha = (
            (
                await check_output(
                    "git",
                    "rev-list",
                    "--reverse",
                    '--after="%s"' % (date,),
                    branch,
                    cwd=repo.directory,
                )
            )
            .strip()
            .split("\n")[0]
        )
    return {"commit": sha}


@config
class GitRepoAuthorLinesForDates:
    pretty: str = field("--pretty:format:$pretty", default="Author:%aN")


@op(
    inputs={
        "repo": git_repository,
        "branch": git_branch,
        "start_end": date_pair,
    },
    outputs={"author_lines": author_line_count},
    config_cls=GitRepoAuthorLinesForDates,
)
async def git_repo_author_lines_for_dates(
    self, repo: Dict[str, str], branch: str, start_end: List[str]
):
    start, end = start_end
    author = ""
    current_work = {}
    proc = await create(
        "git",
        "log",
        "--pretty=format:" + self.parent.config.pretty,
        "--numstat",
        "--before",
        "%s" % (start),
        "--after",
        "%s" % (end),
        branch,
        cwd=repo.directory,
    )
    while not proc.stdout.at_eof():
        line = await proc.stdout.readline()
        line = line.decode(errors="ignore").rstrip()
        if line.startswith("Author:"):
            author = line.split(":")[1]
            if author and author not in current_work:
                current_work[author] = 0
        elif line and author in current_work and line.split()[0].isdigit():
            current_work[author] += int(line.split()[0])
    await stop(proc)
    return {"author_lines": current_work}


def simpsons_diversity_index(*args):
    """
    From https://en.wikipedia.org/wiki/Diversity_index#Simpson_index

    The measure equals the probability that two entities taken at random from
    the dataset of interest represent the same type.
    """
    if len(args) < 2:
        return 0

    def __n_times_n_minus_1(number):
        return number * (number - 1)

    try:
        return int(
            round(
                (
                    1.0
                    - (
                        float(sum(map(__n_times_n_minus_1, args)))
                        / float(sum(args) * (sum(args) - 1))
                    )
                )
                * 100.0
            )
        )
    except ZeroDivisionError:
        return 0


@op(inputs={"author_lines": author_line_count}, outputs={"work": work_spread})
async def work(author_lines: dict):
    return {"work": simpsons_diversity_index(*author_lines.values())}


def git_repo_release_valid_version(tag):
    # Remove v from v1 to make isnumeric return True
    tag = tag.replace("v", "")
    # Make the only separator . instead of - or _
    for replace in ["-", "_"]:
        tag = tag.replace(replace, ".")
    # Make sure there is at least one number in the tag when split by .
    return bool(sum([1 for num in tag.split(".") if num.isnumeric()]))


@op(
    inputs={
        "repo": git_repository,
        "branch": git_branch,
        "start_end": date_pair,
    },
    outputs={"present": release_within_period},
)
async def git_repo_release(
    repo: Dict[str, str], branch: str, start_end: List[str]
):
    """
    Was there a release within this date range
    """
    start, end = start_end
    releases = []
    present = False
    proc = await create(
        "git",
        "log",
        "--tags",
        "--simplify-by-decoration",
        "--pretty=format:%at %D",
        "--before",
        "%s" % (start),
        "--after",
        "%s" % (end),
        branch,
        cwd=repo.directory,
    )
    while not proc.stdout.at_eof() and not present:
        line = await proc.stdout.readline()
        line = line.decode(errors="ignore").strip().split()
        # Check that this is a tag for a release not some random tag
        if line and git_repo_release_valid_version(line[-1]):
            present = True
    await stop(proc)
    return {"present": present}


@op(
    inputs={"repo": git_repository_checked_out},
    outputs={"lines_by_language": lines_by_language_count},
)
async def lines_of_code_by_language(repo: Dict[str, str]):
    """
    This operation relys on ``tokei``. Here's how to install version 10.1.1,
    check it's releases page to make sure you're installing the latest version.

    On Linux

    .. code-block:: console

        $ curl -sSL 'https://github.com/XAMPPRocky/tokei/releases/download/v10.1.1/tokei-v10.1.1-x86_64-apple-darwin.tar.gz' \\
          | tar -xvz && \\
          echo '22699e16e71f07ff805805d26ee86ecb9b1052d7879350f7eb9ed87beb0e6b84fbb512963d01b75cec8e80532e4ea29a tokei' | sha384sum -c - && \\
          sudo mv tokei /usr/local/bin/

    On OSX

    .. code-block:: console

        $ curl -sSL 'https://github.com/XAMPPRocky/tokei/releases/download/v10.1.1/tokei-v10.1.1-x86_64-apple-darwin.tar.gz' \\
          | tar -xvz && \\
          echo '8c8a1d8d8dd4d8bef93dabf5d2f6e27023777f8553393e269765d7ece85e68837cba4374a2615d83f071dfae22ba40e2 tokei' | sha384sum -c - && \\
          sudo mv tokei /usr/local/bin/

    """
    # cloc creates temporary files >:(
    proc = await create("tokei", repo.directory, cwd=repo.directory)
    cols = []
    lines_by_language = {}
    while not proc.stdout.at_eof():
        line = (await proc.stdout.readline()).decode().split()
        if not line or line[0].startswith("-"):
            continue
        if line[0].lower().startswith("lang"):
            cols = [cat.lower() for cat in line[1:]]
            # Tokei -> cloc compatibility
            if "comments" in cols:
                cols[cols.index("comments")] = "comment"
            continue
        if cols:
            header_cols = [word for word in line if not word.isdigit()]
            header = "".join(
                [
                    c
                    for c in "_".join(header_cols).lower()
                    if c.isalpha() or c == "_"
                ]
            )
            # Tokei -> cloc compatibility
            if header == "total":
                header = "sum"
            lines_by_language[header] = dict(
                zip(cols, map(int, line[len(header_cols) :]))
            )
    await stop(proc)
    return {"lines_by_language": lines_by_language}


@op(
    inputs={"langs": lines_by_language_count},
    outputs={"code_to_comment_ratio": language_to_comment_ratio},
)
async def lines_of_code_to_comments(langs: Dict[str, Dict[str, int]]):
    try:
        code_to_comment_ratio = int(
            100
            * langs["sum"]["comment"]
            / (langs["sum"]["comment"] + langs["sum"]["code"])
        )
    except ZeroDivisionError:
        code_to_comment_ratio = 0
    return {"code_to_comment_ratio": code_to_comment_ratio}


@op(
    inputs={
        "repo": git_repository,
        "branch": git_branch,
        "start_end": date_pair,
    },
    outputs={"commits": commit_count},
)
async def git_commits(repo: Dict[str, str], branch: str, start_end: List[str]):
    start, end = start_end
    commit_count = 0
    proc = await create(
        "git",
        "log",
        "--oneline",
        "--before",
        start,
        "--after",
        end,
        branch,
        cwd=repo.directory,
    )
    while not proc.stdout.at_eof():
        line = await proc.stdout.readline()
        if line != b"":
            commit_count += 1
    await stop(proc)
    return {"commits": commit_count}


@op(
    inputs={"author_lines": author_line_count},
    outputs={"authors": author_count},
)
async def count_authors(author_lines: dict):
    return {"authors": len(author_lines.keys())}


@op(inputs={"repo": git_repository}, outputs={}, stage=Stage.CLEANUP)
async def cleanup_git_repo(self, repo: Dict[str, str]):
    if "DFFML_FEATURE_GIT_SKIP_CLEANUP" in os.environ:
        return {}
    # TODO Executor shutil.rmtree
    await run_command(
        ["rm", "-rf", repo.directory], logger=self.logger,
    )
    return {}


"""
`git ls-remote` is a Git command that queries the remote repository for
references, specifically the SHA-1 hashes of commits at the HEADs of branches
and tags. It's frequently utilized to view references without needing to
perform a full clone or fetch.

When done over HTTP/HTTPS, `git ls-remote` follows these steps:

1. **Send a GET request to `<repo URL>/info/refs?service=git-upload-pack`.**

   `git-upload-pack` is the service that's responsible for providing packfiles
    to the client in response to fetch requests. This service also runs the `git
    upload-pack` command, gathering the objects necessary to complete a fetch.

2. **Server will respond with a `text/plain` content type and a `001#
    service=git-upload-pack` header, followed by a list of references and
    capabilities.**

   The payload consists of pkt-line (packet line) formatted data. Each line has
   a 4-byte length header, which includes the 4 bytes used for the length header
   itself. "0000" signals the end of the header.

   The server lists all the HEADs of the branches and the tags of the repo,
   giving their SHA1 values and their fully-qualified names. After the `0000`,
   it also lists `capabilities` such as `multi_ack`, `thin-pack`, `ofs-delta`,
   etc.

3. **Client parses the refs.**

    Your client, or your code using `aiohttp` in this case, would need to parse
    the refs information to extract the SHA-1 hashes and the fully-qualified
    names of the branches and tags.

In short, when you run `git ls-remote` over HTTP, it makes a single HTTP GET
request to the `/info/refs` endpoint of the repository you're querying, and
parses the response to display the list of references in the remote repository.

Remember that this data contains null bytes and other binary data. Thus,
manipulating it as a regular string might result in incorrect results. Use
appropriate methods to deal with binary data.
"""
import os
import sys
import json
import base64
import asyncio
import datetime
import dataclasses
from typing import List, Dict


async def git_ls_remote(session, repo_url):
    import aiohttp

    async with session.get(
        f"{repo_url}/info/refs?service=git-upload-pack",
    ) as response:
        if response.status == 401:
            raise Exception(
                repo_url
                + ": "
                + await response.text()
                + ": "
                + json.dumps(dict(response.headers), indent=4, sort_keys=True)
            )
        elif response.status == 200:
            refs_info = await response.text()
            return parse_refs(repo_url, refs_info)


@dataclasses.dataclass
class GitLsRemoteRefs:
    repo_url: str
    metadata: Dict[str, str]
    capabilities: List[str]
    refs: Dict[str, str]


def parse_refs(repo_url, refs_info):
    if refs_info.count("\n") < 2:
        return
    header, HEAD = refs_info.split("\n", maxsplit=1)
    HEAD, lines = HEAD.split("\x00", maxsplit=1)
    refs = {}
    metadata = {}
    capabilities, lines = lines.split("\n", maxsplit=1)
    metadata_in_capabilities = []
    capabilities = capabilities.split()
    for cap in capabilities:
        if "=" in cap:
            metadata_in_capabilities.append(cap)
            key, value = cap.split("=", maxsplit=1)
            metadata[key] = value
    for cap in metadata_in_capabilities:
        del capabilities[capabilities.index(cap)]
    lines = [HEAD[4:]] + lines.split("\n")
    for line in lines:
        for sep in (" ", "\t"):
            if not line or sep not in line:
                continue
            hash_ref, ref = line.split(sep, maxsplit=1)
            refs[ref] = hash_ref[4:]
            continue
    return GitLsRemoteRefs(
        repo_url=repo_url,
        metadata=metadata,
        capabilities=capabilities,
        refs=refs,
    )


async def git_ls_remotes(repo_urls: List[str], github_token: str = None):
    import aiohttp

    headers = None
    if github_token:
        basic_auth = base64.b64encode(
            ("token:" + github_token).encode()
        ).decode()
        headers = {"Authorization": f"Basic {basic_auth}"}

    async with aiohttp.ClientSession(
        trust_env=True,
        headers=headers,
    ) as session:
        async with asyncio.TaskGroup() as tg:
            for coro in asyncio.as_completed(
                [
                    tg.create_task(git_ls_remote(session, repo_url))
                    for repo_url in repo_urls
                ]
            ):
                git_ls_remote_refs = await coro
                if git_ls_remote_refs:
                    yield git_ls_remote_refs


async def main():
    print(
        json.dumps(
            {
                git_ls_remote_refs.repo_url: dataclasses.asdict(
                    git_ls_remote_refs
                )
                async for git_ls_remote_refs in git_ls_remotes(
                    list(
                        sorted(list(set([line.strip() for line in sys.stdin])))
                    ),
                    github_token=os.environ.get("GH_TOKEN", None),
                )
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
