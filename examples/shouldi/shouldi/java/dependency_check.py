import os
import json
import pathlib
import tempfile
import contextlib
import urllib.parse
from pathlib import Path
from typing import Dict, Any

from dffml import (
    op,
    Definition,
    run_command,
    config,
    field,
    cached_download_unpack_archive,
    prepend_to_path,
)

package_src_dir = Definition(name="package_src_dir", primitive="str")
dependency_check_output = Definition(
    name="dependency_check_output", primitive="Dict[str, Any]"
)


OPENJDK = (
    "https://download.java.net/java/GA/jdk17.0.1/2a2082e5a09d4267845be086888add4f/12/GPL/openjdk-17.0.1_linux-x64_bin.tar.gz",
    "884a8ad424ee1cccc20bd338535064f4223c3421eca62d112ddac871c0a8f8e9ce0c6fb1de81239e4c2776105e298d24",
)
DEPENDENCY_CHECK = (
    "https://github.com/jeremylong/DependencyCheck/releases/download/v6.5.0/dependency-check-6.5.0-release.zip",
    "fae3191f8ca5c8433e9672daef01dee84cfba84dacd0dacb6b73a6016839337929f3e749214924aae0f2dd02a1cf1258",
)


@config
class DependencyCheckConfig:
    openjdk_url: str = field(
        "URL to OpenJDK to run with if java not in PATH", default=OPENJDK[0]
    )
    openjdk_hash: str = field(
        "Hash of OpenJDK to run with if java not in PATH", default=OPENJDK[1]
    )
    dependency_check_url: str = field(
        "URL to OpenJDK to run with if dependency-check.sh not in PATH",
        default=DEPENDENCY_CHECK[0],
    )
    dependency_check_hash: str = field(
        "Hash of Dependency Check to run with if dependency-check.sh not in PATH",
        default=DEPENDENCY_CHECK[1],
    )


def path_to_binary(binary):
    return [
        binary_path
        for binary_path in [
            pathlib.Path(dirname, binary)
            for dirname in os.environ.get("PATH", "").split(":")
        ]
        if binary_path.exists()
    ]


@contextlib.asynccontextmanager
async def ensure_java(self):
    java = path_to_binary("java")
    if java:
        yield str(java[0].resolve())
        return
    with tempfile.TemporaryDirectory() as tempdir:
        tempdir_path = pathlib.Path(tempdir)
        java = await cached_download_unpack_archive(
            self.config.openjdk_url,
            tempdir_path.joinpath("java.tar.gz"),
            tempdir_path.joinpath("java-download"),
            self.config.openjdk_hash,
        )
        java_path = java.joinpath("jdk-17", "bin", "java")
        with prepend_to_path(java_path):
            yield str(java_path)


@contextlib.asynccontextmanager
async def ensure_dependency_check(self):
    dependency_check = path_to_binary("dependency-check.sh")
    if dependency_check:
        yield str(dependency_check[0].resolve())
        return
    with tempfile.TemporaryDirectory() as tempdir:
        tempdir_path = pathlib.Path(tempdir)
        dependency_check_path = await cached_download_unpack_archive(
            self.config.dependency_check_url,
            tempdir_path.joinpath("dependency_check.zip"),
            tempdir_path.joinpath("dependency_check-download"),
            self.config.dependency_check_hash,
        )
        dependency_check_path = dependency_check_path.joinpath(
            "dependency-check", "bin", "dependency-check.sh"
        )
        with prepend_to_path(dependency_check_path.parent):
            dependency_check_path.chmod(0o755)
            yield str(dependency_check_path)


class DependencyCheckError(Exception):
    """
    Raised when dependency-check fails
    """


@op(
    inputs={"pkg": package_src_dir},
    outputs={"report": dependency_check_output},
    imp_enter={
        "depenency_check": ensure_dependency_check,
        "java": ensure_java,
    },
    config_cls=DependencyCheckConfig,
)
async def run_dependency_check(self, pkg: str) -> Dict[str, Any]:
    """
    CLI usage: dffml service dev run -log debug shouldi.dependency_check:run_dependency_check -pkg .
    """
    with tempfile.TemporaryDirectory() as tempdir:
        # Define command
        cmd = [
            "dependency-check.sh",
            "-f",
            "JSON",
            "--out",
            os.path.abspath(tempdir),
        ]
        kwargs = {}
        # Dependency check version 6 requires proxy be set explicitly
        for env_var in ["HTTPS_PROXY", "https_proxy"]:
            if env_var in os.environ:
                parse_result = urllib.parse.urlparse(os.environ[env_var])
                cmd += [
                    "--proxyserver",
                    parse_result.hostname,
                    "--proxyport",
                    str(parse_result.port)
                    if parse_result.port is not None
                    else "8080",
                ]
                break
        # Directory or file to scan
        cmd.append("-s")
        if Path(pkg).is_file():
            cmd.append(os.path.basename(pkg))
            kwargs["cwd"] = os.path.dirname(pkg)
        else:
            cmd.append(".")
            kwargs["cwd"] = pkg
        # Run command
        try:
            await run_command(cmd, logger=self.logger, **kwargs)
        except RuntimeError as e:
            raise DependencyCheckError from e

        report_contents = pathlib.Path(
            tempdir, "dependency-check-report.json"
        ).read_text()
        dependency_check_op = json.loads(report_contents)

    t_result = []
    for items in dependency_check_op["dependencies"]:
        t_result += items["vulnerabilities"]

    final_report = {}
    score = 0
    for item in t_result:
        final_report["name"] = item["name"]
        final_report["severity"] = item["severity"]
        score += 1
    final_report["total_CVE"] = score
    final_report["original_report"] = dependency_check_op

    return {"report": final_report}
