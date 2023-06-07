import pathlib
import logging
import platform
from typing import NewType

import dffml
from dffml_operations_innersource.npm_groovy_lint import JavaBinary


class _JAVA_USE_DEFAULT_PLATFORM_URLS:
    pass


class _JAVA_USE_DEFAULT_CACHE_DIR:
    pass


JavaCacheDir = NewType("JavaCacheDir", str)
JavaPlatformURLs = NewType("JavaPlatformURLs", str)


JAVA_USE_DEFAULT_CACHE_DIR = _JAVA_USE_DEFAULT_CACHE_DIR()
JAVA_DEFAULT_CACHE_DIR_PARTS = (
    ".tools", "open-architecture", "innersource", ".cache", "java",
)
JAVA_USE_DEFAULT_PLATFORM_URLS = _JAVA_USE_DEFAULT_PLATFORM_URLS()
JAVA_DEFAULT_PLATFORM_URLS = {
    "Linux": {
        "url": "https://download.oracle.com/java/17/latest/jdk-17_linux-x64_bin.tar.gz",
        "expected_hash": "2b5a966e5ea1b6cb47f5b6d3a806a176b71783896ff2f837a0a6bfe8f5e9dec12046e524f57702d34d93196636a74d19",
    },
}


# IN PROGRESS XXX We are now going to try enabling this as an overlay.
# If this works we'll create a seperate package to enable these for the install.
# Or maybe we'll do a service dev command to create the package ad-hoc.
# Could also do ad-hoc package creation for seed inputs via flow which loads
# from importlib.resources a JSON seed value (or any format).
async def ensure_java(
    cache_dir: JavaCacheDir = JAVA_USE_DEFAULT_CACHE_DIR,
    platform_urls: JavaPlatformURLs = JAVA_USE_DEFAULT_PLATFORM_URLS,
    *,
    env: dict = None,
    logger: logging.Logger = None,
) -> JavaBinary:
    # Download via given platform to download mapping or use default
    if platform_urls is JAVA_USE_DEFAULT_PLATFORM_URLS:
        platform_urls = JAVA_DEFAULT_PLATFORM_URLS
    # Store in given cache directory or create default relative to cwd
    if cache_dir is JAVA_USE_DEFAULT_CACHE_DIR:
        cache_dir = pathlib.Path(*JAVA_DEFAULT_CACHE_DIR_PARTS)
    # Download node
    java_install_path = await dffml.cached_download_unpack_archive(
        **{
            "file_path": cache_dir.joinpath("java.tar.gz"),
            "directory_path": cache_dir.joinpath("java-download"),
            # Use whatever values are appropriate for the system we are on
            **platform_urls[platform.system()],
        }
    )
    # Find the binary
    java_bin_path = [
        path.parent
        for path in java_install_path.rglob("java")
        if path.parent.name == "bin"
    ][0]
    with dffml.prepend_to_path(java_bin_path, env):
        pass
    return java_bin_path.joinpath("java")

