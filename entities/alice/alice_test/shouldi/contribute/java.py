import pathlib
import logging
import platform
from typing import NewType

import dffml
from dffml_operations_innersource.operations import JavaBinary


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
        "url": "https://download.java.net/java/GA/jdk19.0.1/afdd2e245b014143b62ccb916125e3ce/10/GPL/openjdk-19.0.1_linux-x64_bin.tar.gz",
        "expected_hash": "ec79c3f085c295876f96d38bfaece0c565ff89152928d71a8b6bf1baf9eda2f27ce6cd857612a4e73540e67c1c0229b5",
    },
}


# TODO Move these ensure_ functions into which can then be overlayed as desired
# via CLI or via install of ad-hoc blank package with only entry_points.txt to
# enable them as desired.
# alice_test.shouldi.contribute.bom_v0_0_0
# This is our reference flow, which knows how to understand, analyize, work in,
# and rebuild itself from anywhere. This allows us to get developers developing
# on alice, or any overlays to alice (being anything else you need to work on or
# analyze). We communicate via ATProto threads to post replys with verifiable
# credentials where the crendential manifest had a SCITT receipt which itself
# appears in a SCITT thread, where the root is the root of trust for that SCITT
# instance.
# IN PROGRESS XXX We are now going to try enabling this as an overlay.
# If this works we'll create a seperate package to enable these for the install.
# Or maybe we'll do a service dev command to create the package ad-hoc.
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

