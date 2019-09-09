import io
import os
import sys
import abc
import glob
import json
import uuid
import shutil
import inspect
import asyncio
import hashlib
import tempfile
import unittest
import itertools
import subprocess
import collections
import asyncio.subprocess
from itertools import product
from datetime import datetime
from contextlib import asynccontextmanager, AsyncExitStack
from typing import (
    AsyncIterator,
    Dict,
    List,
    Tuple,
    Any,
    NamedTuple,
    Union,
    get_type_hints,
    NewType,
    Optional,
    Set,
    Iterator,
)

from dateutil.relativedelta import relativedelta

from dffml.df.types import Stage
from dffml.df.base import op

from .definitions import *

from dffml_feature_git.util.proc import check_output, create, stop, inpath

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
    inputs={"URL": URL},
    outputs={"repo": git_repository},
    conditions=[valid_git_repository_URL],
)
async def clone_git_repo(URL: str):
    directory = tempfile.mkdtemp(prefix="dffml-feature-git-")
    exit_code = await exec_with_logging("git", "clone", URL, directory)
    if exit_code != 0:
        shutil.rmtree(repo["directory"])
        raise RuntimeError("Failed to clone git repo %r" % (URL,))

    return {"repo": {"URL": URL, "directory": directory}}


@op(
    inputs={"repo": git_repository},
    outputs={"branch": git_branch},
    conditions=[no_git_branch_given],
)
async def git_repo_default_branch(repo: Dict[str, str]):
    branches = (
        await check_output("git", "branch", "-r", cwd=repo["directory"])
    ).split("\n")
    main = [branch for branch in branches if "->" in branch][0].split()[-1]
    main = main.split("/")[-1]
    return {"branch": main}


@op(
    inputs={"repo": git_repository, "commit": git_commit},
    outputs={"repo": git_repository_checked_out},
)
async def git_repo_checkout(repo: Dict[str, str], commit: str):
    await check_output("git", "checkout", commit, cwd=repo["directory"])
    # NOTE Don't modify variables which are mearly references! This will create
    # more permutations than intended.
    checked_out = repo.copy()
    checked_out["commit"] = commit
    return {"repo": checked_out}


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
            cwd=repo["directory"],
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
                    cwd=repo["directory"],
                )
            )
            .strip()
            .split("\n")[0]
        )
    return {"commit": sha}


@op(
    inputs={
        "repo": git_repository,
        "branch": git_branch,
        "start_end": date_pair,
    },
    outputs={"author_lines": author_line_count},
)
async def git_repo_author_lines_for_dates(
    repo: Dict[str, str], branch: str, start_end: List[str]
):
    start, end = start_end
    author = ""
    current_work = {}
    proc = await create(
        "git",
        "log",
        "--pretty=format:Author:%aN",
        "--numstat",
        "--before",
        "%s" % (start),
        "--after",
        "%s" % (end),
        branch,
        cwd=repo["directory"],
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
    # Make the only seperator . instead of - or _
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
        cwd=repo["directory"],
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
    # cloc creates temporary files >:(
    proc = await create("tokei", repo["directory"], cwd=repo["directory"])
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
        cwd=repo["directory"],
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
async def cleanup_git_repo(repo: Dict[str, str]):
    shutil.rmtree(repo["directory"])
    return {}
