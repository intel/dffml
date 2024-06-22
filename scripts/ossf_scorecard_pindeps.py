import os
import sys
import json
import copy
import shlex
import pathlib
import functools
import dataclasses
import urllib.request
from typing import List, Optional

from pydantic import BaseModel


import snoop

SRCROOT = pathlib.Path(__file__).parents[1]


@functools.cache
def pypi_package_json(package: str) -> dict:
    with urllib.request.urlopen(
        f"https://pypi.org/pypi/{package}/json"
    ) as resp:  # skipcq: BAN-B310
        return json.load(resp)


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
        if cmd[i - 1] != "-e" and not arg.startswith("-")
    ]

    for i, package_name in enumerate(packages):
        if (
            not package_name.strip()
            or package_name.startswith("http://")
            or package_name.startswith("https://")
            or package_name.startswith("git+")
            or "==" in package_name
        ):
            continue

        package_json = pypi_package_json(package_name.split("[")[0])

        pypi_latest_package_version = package_json["info"]["version"]

        for release_dict in package_json["releases"][
            pypi_latest_package_version
        ]:
            cmd.insert(
                cmd.index(package_name, i_install + 1) + 2,
                f'--hash=sha256:{release_dict["digests"]["sha256"]}',
            )

        cmd[
            cmd.index(package_name, i_install + 1)
        ] = f"{package_name}=={pypi_latest_package_version}"
    return cmd


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


def main():
    for event, result in get_sarif_results(json.load(sys.stdin)):
        for location in result.locations:
            pip_install_command = shlex.split(
                location.physicalLocation.region.snippet.text
            )
            pinned_pip_install_command = pin_packages(pip_install_command)
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
            new_lines = []
            for line_number, line in enumerate(path.read_text().split("\n")):
                if (
                    line_number >= location.physicalLocation.region.startLine
                    and line_number <= location.physicalLocation.region.endLine
                    and location.physicalLocation.region.snippet.text in line
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
                        line = (
                            line_start
                            + shlex.join(pinned_pip_install_command)
                            + line_end
                        )
                        snoop.pp(location.physicalLocation, line_number, line)
                new_lines.append(line)
            path.write_text("\n".join(new_lines))


if __name__ == "__main__":
    main()
