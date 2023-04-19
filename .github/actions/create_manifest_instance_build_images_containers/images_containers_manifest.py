#!/usr/bin/env python
# This file generates a manifest for building container images
# Usage: JSON_INDENT="    " nodemon -e py,Dockerfile,HEAD --exec 'clear; python scripts/images_containers_manifest.py; test 1'
import os
import sys
import json
import pathlib
import itertools
import traceback
import subprocess
import urllib.request


def path_to_image_name(path, root_path):
    # Stem as image name
    if path.stem != "Dockerfile":
        return path.stem
    # Non-top level no stem as image name (filename is Dockerfile)
    hyphen_dir_path = str(path.parent.relative_to(root_path)).replace(os.sep, "-").replace(".", "").replace("_", "-")
    if hyphen_dir_path != "." and hyphen_dir_path != "":
        return hyphen_dir_path
    # Top level dir Dockerfile use top level dirname
    if "GITHUB_WORKSPACE" in os.environ:
        # Use repository name if running in workspace
        return os.environ["OWNER_REPOSITORY"].split("/")[-1]
    return str(root_path.resolve().name)


def main():
    # For running under GitHub actions within a container
    if "GITHUB_WORKSPACE" in os.environ:
        subprocess.check_call(["git", "config", "--global", "--add", "safe.directory", os.environ["GITHUB_WORKSPACE"]])

    try:
        os.environ.update({
            "COMMIT": subprocess.check_output(["git", "log", "-n", "1", "--format=%H"]).decode().strip(),
        })
    except:
        traceback.print_exc(file=sys.stderr)

    try:
        os.environ.update({
            "ROOT_PATH": str(pathlib.Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"]).decode().strip()).relative_to(os.getcwd())),
            "SCHEMA": "https://github.com/intel/dffml/raw/c82f7ddd29a00d24217c50370907c281c4b5b54d/schema/github/actions/build/images/containers/0.0.0.schema.json",
            "OWNER_REPOSITORY": "/".join(subprocess.check_output(["git", "remote", "get-url", "origin"]).decode().strip().replace(".git", "").split("/")[-2:]),
            "BRANCH": subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode().strip(),
            "PREFIX": os.environ.get("PREFIX", json.dumps([
                ".",
                "scripts",
                "dffml/skel/operations",
            ])),
            "NO_DELTA_PREFIX": os.environ.get("NO_DELTA_PREFIX", json.dumps([
                ".",
                "scripts",
                "dffml/skel/operations",
            ])),
        })
    except:
        traceback.print_exc(file=sys.stderr)

    # Pull request file change delta filter using GitHub API
    prefixes = json.loads(os.environ["PREFIX"])
    no_delta_prefixes = json.loads(os.environ["NO_DELTA_PREFIX"])
    owner, repository = os.environ["OWNER_REPOSITORY"].split("/", maxsplit=1)
    base = None
    env_vars = ["BASE", "BASE_REF"]
    for env_var in env_vars:
        if env_var in os.environ and os.environ[env_var].strip():
            # Set if present and not blank
            base = os.environ[env_var]

    # Empty manifest (list of manifests for each build file) in case not triggered
    # from on file change (workflow changed or dispatched).
    manifest = []
    # Path to root of repo
    root_path = pathlib.Path(os.environ["ROOT_PATH"])
    # Grab commit from git
    commit = os.environ["COMMIT"]
    if base is not None:
        if "GITHUB_DELTA_RESPONSE_JSON" in os.environ:
            response_json = json.loads(os.environ["GITHUB_DELTA_RESPONSE_JSON"])
        else:
            compare_url = os.environ["COMPARE_URL"]
            compare_url = compare_url.replace("{base}", base)
            compare_url = compare_url.replace("{head}", os.environ["HEAD"])
            with urllib.request.urlopen(
                urllib.request.Request(
                    compare_url,
                    headers={
                        "Authorization": "bearer " + os.environ["GH_ACCESS_TOKEN"],
                    },
                )
            ) as response:
                response_json = json.load(response)
        # Print for debug
        print(json.dumps({
            "@context": {
                "@vocab": "github_delta_response_json",
            },
            **response_json,
        }, sort_keys=True, indent=4), file=sys.stderr)
        # Build the most recent commit
        commit = response_json["commits"][-1]["sha"]
        manifest = list(itertools.chain(*(
            [
                [
                    {
                        "image_name": path_to_image_name(path, root_path),
                        "dockerfile": str(path.relative_to(root_path)),
                        "owner": owner,
                        "repository": repository,
                        "branch": os.environ["BRANCH"],
                        "commit": commit,
                    }
                    for path in [
                        pathlib.Path(compare_file["filename"])
                        for compare_file in response_json["files"]
                        if (
                            any([
                                (
                                    (
                                        pathlib.Path(compare_file["filename"]).parent.name == ""
                                        and prefix_path == "."
                                    )
                                    or pathlib.Path(compare_file["filename"]).parent.name == prefix_path
                                )
                                for prefix_path in prefixes
                            ]) and compare_file["filename"].endswith("Dockerfile")
                        )
                    ]
                ]
            ] + [
                [
                    json.loads(path.read_text())
                    for path in [
                        pathlib.Path(compare_file["filename"])
                        for compare_file in response_json["files"]
                        if (
                            any([
                                (
                                    (
                                        pathlib.Path(compare_file["filename"]).parent.name == ""
                                        and prefix_path == "."
                                    )
                                    or pathlib.Path(compare_file["filename"]).parent.name == prefix_path
                                )
                                for prefix_path in prefixes
                            ]) and compare_file["filename"].endswith("manifest.json")
                        )
                    ]
                ]
            ]
        )))
    else:
        print(f"::notice file={__file__},line=1,endLine=1,title=nobase::None of {env_vars!r} found in os.environ", file=sys.stderr)
        manifest = list(itertools.chain(*(
            [
                [
                    {
                        "image_name": path_to_image_name(path, root_path),
                        "dockerfile": str(path.relative_to(root_path)),
                        "owner": owner,
                        "repository": repository,
                        "branch": os.environ["BRANCH"],
                        "commit": commit,
                    }
                    for path in prefix_path.glob("*Dockerfile")
                ]
                for prefix_path in map(pathlib.Path, prefixes)
                if any(
                    str(prefix_path.relative_to(root_path)) in no_delta_prefix
                    for no_delta_prefix in no_delta_prefixes
                )
            ] + [
                [
                    json.loads(path.read_text())
                    for path in prefix_path.glob("*manifest.json")
                ]
                for prefix_path in map(pathlib.Path, prefixes)
                if any(
                    str(prefix_path.relative_to(root_path)) in no_delta_prefix
                    for no_delta_prefix in no_delta_prefixes
                )
            ]
        )))

    # Add proxies or other runtime args/env vars
    for i in manifest:
        build_args = {}
        if "build_args" in i:
            build_args = dict(json.loads(i["build_args"]))
        for env_var in [
            "HTTP_PROXY",
            "HTTPS_PROXY",
            "NO_PROXY",
        ]:
            if not env_var in os.environ:
                continue
            build_args[env_var] = os.environ[env_var]
        i["build_args"] = json.dumps(list(build_args.items()))

    github_actions_manifest = {
        "include": manifest,
    }
    json_ld_manifest = {
        "@context": {
            "@vocab": os.environ["SCHEMA"],
        },
        **github_actions_manifest,
    }
    print(json.dumps(json_ld_manifest, sort_keys=True, indent=os.environ.get("JSON_INDENT", None)))

    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as fileobj:
            fileobj.write(f"manifest={json.dumps(manifest)}\n")
            fileobj.write(f'github_actions_manifest={json.dumps(github_actions_manifest)}\n')

if __name__ == "__main__":
    main()
