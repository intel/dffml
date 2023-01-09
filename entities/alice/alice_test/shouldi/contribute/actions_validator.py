import pathlib
import platform
from typing import NewType

import dffml
from dffml_operations_innersource.operations import ActionsValidatorBinary


class _ACTIONS_VALIDATOR_USE_DEFAULT_PLATFORM_URLS:
    pass


class _ACTIONS_VALIDATOR_USE_DEFAULT_CACHE_DIR:
    pass


ActionsValidatorCacheDir = NewType("ActionsValidatorCacheDir", str)
ActionsValidatorPlatformURLs = NewType("ActionsValidatorPlatformURLs", str)

ACTIONS_VALIDATOR_DEFAULT_BINARY = "actions-validator"
ACTIONS_VALIDATOR_USE_DEFAULT_CACHE_DIR = _ACTIONS_VALIDATOR_USE_DEFAULT_CACHE_DIR()
ACTIONS_VALIDATOR_DEFAULT_CACHE_DIR_PARTS = (
    ".tools", "open-architecture", "innersource", ".cache", "actions-validator",
)
ACTIONS_VALIDATOR_USE_DEFAULT_PLATFORM_URLS = _ACTIONS_VALIDATOR_USE_DEFAULT_PLATFORM_URLS()
# TODO Load platform URL defaults from an SBOM. Enabling full circle, scan via
# cve-bin-tool to produce / handle VEX. Alice help issue VDR via DAC, EAT.
ACTIONS_VALIDATOR_DEFAULT_PLATFORM_URLS = {
    "Linux": {
        "url": "https://github.com/mpalmer/action-validator/releases/download/v0.2.1/action-validator_linux_amd64",
        "expected_hash": "17d21449f31090efa13fc009be3181121f7c2c4fbe4618b84f4ac66d6bd9ffce21f76193879ddac0f3eec90fe5841280",
    },
}


async def ensure_actions_validator(
    cache_dir: ActionsValidatorCacheDir = ACTIONS_VALIDATOR_USE_DEFAULT_CACHE_DIR,
    platform_urls: ActionsValidatorPlatformURLs = ACTIONS_VALIDATOR_USE_DEFAULT_PLATFORM_URLS,
) -> ActionsValidatorBinary:
    """

    - References

        - Original sketch of system context with inputs as allow list

            - https://youtu.be/m0TO9IOqRfQ?t=2373&list=PLtzAOVTpO2jaHsS4o-sDzDyHEug-1KRbK
    - TODOs

        - This operation should be added to the flow during dynamic overlay
          application. Once we have the system context allow list working which
          will tell us which inputs are allowed from which origins (seed,
          client, etc. (see references above for system context sketch).
          At that point, within dynamic overlay application we will inspect the
          system context allow list while we are in the data flow as class
          method construction or whole context call construction to determine if
          the binary is allowed to be passed from caller to callee flow. If it
          does not appear in the allow list, then we will overlay this
          operation. This is a variation on our static overlay, where we apply
          no matter what. In this case, this operation is it's own overlay which
          is applied only if the input is not in the allow list.
    """
    actions_validator_binary_path = pathlib.Path(ACTIONS_VALIDATOR_DEFAULT_BINARY)
    # Ensure we have a copy of the binary
    if (
        not actions_validator_binary_path.exists()
        or not dffml.inpath(actions_validator_binary_path)
    ):
        # Download via given platform to download mapping or use default
        if platform_urls is ACTIONS_VALIDATOR_USE_DEFAULT_PLATFORM_URLS:
            platform_urls = ACTIONS_VALIDATOR_DEFAULT_PLATFORM_URLS
        # Store in given cache directory or create default relative to cwd
        if cache_dir is ACTIONS_VALIDATOR_USE_DEFAULT_CACHE_DIR:
            cache_dir = pathlib.Path(*ACTIONS_VALIDATOR_DEFAULT_CACHE_DIR_PARTS)
        # We don't have a copy of the binary in the path, download it to cache
        actions_validator_binary_path = await dffml.cached_download(
            **{
                "target_path": cache_dir.joinpath("actions-validator"),
                "chmod": 0o755,
                # Use whatever values are appropriate for the system we are on
                **platform_urls[platform.system()],
            }
        )
    return actions_validator_binary_path.resolve()
