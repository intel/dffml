import pathlib
import logging
import platform
from typing import NewType

import dffml
from dffml_operations_innersource.npm_groovy_lint import NPMGroovyLintCMD


class _NPM_GROOVY_LINT_USE_DEFAULT_PLATFORM_URLS:
    pass


class _NPM_GROOVY_LINT_USE_DEFAULT_CACHE_DIR:
    pass


NPMGroovyLintCacheDir = NewType("NPMGroovyLintCacheDir", str)
NPMGroovyLintPlatformURLs = NewType("NPMGroovyLintPlatformURLs", str)


NPM_GROOVY_LINT_DEFAULT_BINARY = "npm-groovy-lint"
NPM_GROOVY_LINT_USE_DEFAULT_CACHE_DIR = _NPM_GROOVY_LINT_USE_DEFAULT_CACHE_DIR()
NPM_GROOVY_LINT_DEFAULT_CACHE_DIR_PARTS = (
    ".tools", "open-architecture", "innersource", ".cache", "npm-groovy-lint",
)
NPM_GROOVY_LINT_USE_DEFAULT_PLATFORM_URLS = _NPM_GROOVY_LINT_USE_DEFAULT_PLATFORM_URLS()
# TODO Load all these from a json file using importlib.resources within test bom
NPM_GROOVY_LINT_DEFAULT_PLATFORM_URLS = {
    "Linux": {
        "url": "https://nodejs.org/dist/v18.13.0/node-v18.13.0-linux-x64.tar.xz",
        "expected_hash": "e90a56e93846d38404a79fd1f023524dbc3e9528f6b14d14a558c7c4499157b54e05c4bc5b2ed8ee0baaba310938502d",
    },
}


async def ensure_npm_groovy_lint(
    cache_dir: NPMGroovyLintCacheDir = NPM_GROOVY_LINT_USE_DEFAULT_CACHE_DIR,
    platform_urls: NPMGroovyLintPlatformURLs = NPM_GROOVY_LINT_USE_DEFAULT_PLATFORM_URLS,
    *,
    env: dict = None,
    logger: logging.Logger = None,
) -> NPMGroovyLintCMD:
    # TODO Take node as arg from ensure_node
    # The location we'll assume the binary is at, its basename, resolved on exec
    # to determine correct path.
    npm_groovy_lint_binary_path = pathlib.Path(NPM_GROOVY_LINT_DEFAULT_BINARY)
    # Bail out if we already have a copy of the binary available in the path,
    # aka that subprocess -> fork + exec will succeed.
    if dffml.inpath(npm_groovy_lint_binary_path.name):
        return [dffml.which(npm_groovy_lint_binary_path.name)]
    if (
        npm_groovy_lint_binary_path.exists()
        or (
            dffml.inpath(npm_groovy_lint_binary_path)
            and dffml.inpath("node")
        )
    ):
        return ["node", npm_groovy_lint_binary_path]
    # Download via given platform to download mapping or use default
    if platform_urls is NPM_GROOVY_LINT_USE_DEFAULT_PLATFORM_URLS:
        platform_urls = NPM_GROOVY_LINT_DEFAULT_PLATFORM_URLS
    # Store in given cache directory or create default relative to cwd
    if cache_dir is NPM_GROOVY_LINT_USE_DEFAULT_CACHE_DIR:
        cache_dir = pathlib.Path(*NPM_GROOVY_LINT_DEFAULT_CACHE_DIR_PARTS)
    # Download node
    node_install_path = await dffml.cached_download_unpack_archive(
        **{
            "file_path": cache_dir.joinpath("node.tar.gz"),
            "directory_path": cache_dir.joinpath("node-download"),
            # Use whatever values are appropriate for the system we are on
            **platform_urls[platform.system()],
        }
    )
    # Find the binary for nodejs
    node_bin_path = [
        path
        for path in node_install_path.rglob("node")
        if path.parent.name == "bin"
    ][0]
    # Find the binary for npm
    npm_bin_path = [
        path
        for path in node_install_path.rglob("npm")
        if path.parent.name == "bin"
    ][0]
    # Ensure node binary is in path before calling npm to install
    with dffml.prepend_to_path(*node_bin_path.parent.resolve().parts, env):
        # Run npm to install the package with the binary we are wrapping.
        # Install to the cache dir.
        # In this case npm-groovy-lint
        async for event, result in dffml.run_command_events(
            [
                node_bin_path,
                npm_bin_path,
                "i",
                "npm-groovy-lint",
            ],
            cwd=cache_dir,
            env=env,
            logger=logger,
        ):
            pass
        # Create the path to the binary we installed
        node_modules_bin_path = cache_dir.joinpath(
            "node_modules", ".bin",
        ).resolve()
        # Add it to the path. Do not resolve because it might be an exec symlink
        with dffml.prepend_to_path(*node_modules_bin_path.parts, env):
            pass
        return [node_bin_path, node_modules_bin_path.joinpath("npm-groovy-lint")]
