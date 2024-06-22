import os
import sys
import json
import copy
import shlex
import shutil
import tarfile
import zipfile
import pathlib
import textwrap
import tempfile
import functools
import subprocess
import dataclasses
import urllib.request
from typing import List, Optional

import tomli_w
import cachier
from pydantic import BaseModel


import snoop

SRCROOT = pathlib.Path(__file__).parents[1]


@functools.cache
def pypi_package_json(package: str) -> dict:
    with urllib.request.urlopen(
        f"https://pypi.org/pypi/{package}/json"
    ) as resp:  # skipcq: BAN-B310
        return json.load(resp)


# Remove tempdir from cache
@cachier.cachier(hash_func=lambda args, kwargs: kwargs["url"])
def find_package_name_from_zip(tempdir, url):
    # - Download the package
    # - Run sys.executable -m build . on the package
    # - Read `Name: return this-value` from `dist/*.tar.gz/*/PKG-INFO
    url_parsed = urllib.parse.urlparse(url, allow_fragments=True)
    if url_parsed.fragment:
        fragment = urllib.parse.parse_qs(url_parsed.fragment)

        if "egg" in fragment:
            return fragment["egg"][0]

        if "subdiretory" in fragment:
            raise NotImplementedError("subdirectory within URL fragment (#)")

    package_zip_path = tempdir.joinpath("package.zip")
    package_path = tempdir.joinpath("package")
    with open(
        package_zip_path,
        "wb",
    ) as zip_fileobj, urllib.request.urlopen(
        url,
    ) as resp:  # skipcq: BAN-B310
        shutil.copyfileobj(resp, zip_fileobj)

    with zipfile.ZipFile(package_zip_path) as zipfileobj:
        zipfileobj.extractall(path=package_path)

    package_path = list(package_path.glob("*"))[0]
    built_package_path = tempdir.joinpath("built_package")

    cmd = [
        sys.executable,
        "-m",
        "build",
        ".",
    ]
    subprocess.check_call(cmd, cwd=package_path)

    built_package_zip_path = list(package_path.joinpath("dist").glob("*.whl"))[
        0
    ]

    with zipfile.ZipFile(built_package_zip_path) as zipfileobj:
        zipfileobj.extractall(path=built_package_path)

    built_package_pkg_info_path = list(built_package_path.glob("*.dist-info"))[
        0
    ].joinpath(
        "METADATA",
    )

    return list(
        [
            line.split(":", maxsplit=1)[1]
            for line in built_package_pkg_info_path.read_text().split("\n")
            if line.startswith("Name:")
        ]
    )[0].strip()


@snoop
@cachier.cachier(hash_func=lambda args, kwargs: shlex.join(kwargs["cmd"]))
def pin_packages(cmd):
    cmd = copy.copy(cmd)
    i_install = cmd.index("install")
    editable_packages = [
        arg
        for i, arg in enumerate(cmd[i_install + 1 :], start=i_install + 1)
        if cmd[i - 1] == "-e" and not arg.startswith("-")
    ]
    packages = [
        arg
        for i, arg in enumerate(cmd[i_install + 1 :], start=i_install + 1)
        if cmd[i - 1] != "-e" and not arg.startswith("-") and arg.strip()
    ]
    if "-U" in cmd:
        cmd.remove("-U")
    if "--upgrade" in cmd:
        cmd.remove("--upgrade")

    for i, package_name in enumerate(packages):
        if (
            not package_name.strip()
            or "http://" in package_name
            or "https://" in package_name
            or "==" in package_name
        ):
            continue

        package_json = pypi_package_json(package_name.split("[")[0])

        pypi_latest_package_version = package_json["info"]["version"]

        packages[
            packages.index(package_name)
        ] = f"{package_name}=={pypi_latest_package_version}"

    with tempfile.TemporaryDirectory() as tempdir:
        tempdir = pathlib.Path(tempdir)
        if not packages:
            return None

        pyproject_toml_dir_path = tempdir.joinpath("pyproject-gen")
        pyproject_toml_dir_path.mkdir()
        pyproject_toml_path = pyproject_toml_dir_path.joinpath(
            "pyproject.toml"
        )
        pyproject_toml_path.write_text(
            tomli_w.dumps(
                {
                    "build-system": {
                        "requires": ["setuptools >= 61.0"],
                        "build-backend": "setuptools.build_meta",
                    },
                    "project": {
                        "name": "pip-tools-compile-pin-deps",
                        "version": "1.0.0",
                        "dependencies": [
                            *editable_packages,
                            *[
                                (
                                    arg
                                    if not ".zip" in arg and not "://" in arg
                                    else f"{find_package_name_from_zip(tempdir, arg)} @ {arg}"
                                )
                                for arg in packages
                                if "==" not in arg and "$" not in arg
                            ],
                        ],
                    },
                },
            )
        )

        print(pyproject_toml_path.read_text())

        cmd = [
            sys.executable,
            "-m",
            "piptools",
            "compile",
            "--generate-hashes",
            str(pyproject_toml_path.resolve()),
        ]
        return subprocess.check_output(
            cmd,
        )


class Snippet(BaseModel):
    text: str


class Region(BaseModel):
    startLine: int
    endLine: int = None
    snippet: Snippet = None


class ArtifactLocation(BaseModel):
    uri: str
    uriBaseId: str


class PhysicalLocation(BaseModel):
    region: Region
    artifactLocation: ArtifactLocation


class LocationMessage(BaseModel):
    text: str


class Location(BaseModel):
    physicalLocation: PhysicalLocation
    message: LocationMessage = None


class Message(BaseModel):
    text: str


class Rule(BaseModel):
    ruleId: str
    ruleIndex: int
    message: Message
    locations: List[Location]


def get_sarif_results(ossf_scorecard_sarif):
    for run in ossf_scorecard_sarif["runs"]:
        for result_dict in run["results"][::-1]:
            result = Rule(**result_dict)
            event_subject_object = {
                "ruleId": result.ruleId,
            }
            # TODO event_subject = ":".join(... dict(sorted(event_subject_object.items())))
            event_subject = None
            # if result.ruleId == "PinnedDependenciesID":
            # snoop.pp(result.locations[0])
            if result.locations[0].message is not None:
                # TODO Container pinning etc.
                if "downloadThenRun" in result.locations[0].message.text:
                    pass
                elif "containerImage" in result.locations[0].message.text:
                    pass
                else:
                    yield event_subject, result

@snoop
def main():
    ran = False

    for event, result in get_sarif_results(json.load(sys.stdin)):
        for location in result.locations:
            if (
                location.physicalLocation.artifactLocation.uriBaseId
                != "%SRCROOT%"
            ):
                raise FileNotFoundError(
                    str(location.physicalLocation.artifactLocation)
                )
            path = SRCROOT.joinpath(
                location.physicalLocation.artifactLocation.uri
            )
            if not path.is_file():
                raise FileNotFoundError(path)

            snippet = location.physicalLocation.region.snippet

            lines = path.read_text().split("\n")

            env = {}
            for line_number, line in enumerate(lines):
                if "export " in line and "=" in line:
                    key, value = (
                        line.split("export ", maxsplit=1)[1]
                        .strip()
                        .split("=", maxsplit=1)
                    )
                    env[key] = value

            for env_var_name, replace in env.items():
                for find in [
                    "$" + env_var_name,
                    "${" + env_var_name + "}",
                ]:
                    if find in snippet.text:
                        snippet.text = snippet.text.replace(find, replace)

            pip_install_command = shlex.split(snippet.text)
            pinned_pip_install_command = pin_packages(pip_install_command)
            if pinned_pip_install_command is None:
                snoop.pp("Nothing we can do here", pip_install_command)
                continue

            new_lines = []
            for line_number, line in enumerate(lines):
                if (
                    line_number >= location.physicalLocation.region.startLine
                    and line_number <= location.physicalLocation.region.endLine
                    and snippet.text in line
                ):
                    with snoop():
                        line_start = line[: line.index(pip_install_command[0])]
                        i_line_end = len(line_start) + 1
                        while pip_install_command[-1] in line[
                            i_line_end:
                        ] and line.index(pip_install_command[-1], i_line_end):
                            i_line_end = line.index(
                                pip_install_command[-1], i_line_end
                            ) + len(pip_install_command[-1])
                        line_end = line[i_line_end:]
                        shlex.join(pinned_pip_install_command)
                        new_lines.append(
                            line_start
                            + shlex.join(
                                [
                                    "echo",
                                    "-e",
                                    pinned_pip_install_command,
                                    "|",
                                    "tee",
                                    "requirements-lock.txt",
                                ]
                            )
                            + line_end
                        )
                        line = line_start + "python -m pip install -r requirements-lock.txt" + line_end
                        snoop.pp(new_lines[-1], line)
                        snoop.pp(location.physicalLocation, line_number, line)

                        # XXX DEBUG
                        ran = True
                new_lines.append(line)
            path.write_text("\n".join(new_lines))

            if ran:
                break
        if ran:
            break


if __name__ == "__main__":
    main()
