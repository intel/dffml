import os
import importlib.util
from setuptools import setup

# Boilerplate to load commonalities
spec = importlib.util.spec_from_file_location(
    "setup_common", os.path.join(os.path.dirname(__file__), "setup_common.py")
)
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)

common.KWARGS["entry_points"] = {
    "dffml.operation": [
        f"get_url_from_payload = {common.IMPORT_NAME}.operations:get_url_from_payload",
        f"check_if_default_branch = {common.IMPORT_NAME}.operations:check_if_default_branch",
        f"get_image_tag = {common.IMPORT_NAME}.operations:get_image_tag",
        f"get_running_containers = {common.IMPORT_NAME}.operations:get_running_containers",
        f"get_status_running_containers = {common.IMPORT_NAME}.operations:get_status_running_containers",
        f"parse_docker_commands = {common.IMPORT_NAME}.operations:parse_docker_commands",
        f"docker_build_image = {common.IMPORT_NAME}.operations:docker_build_image",
        f"restart_running_containers = {common.IMPORT_NAME}.operations:restart_running_containers",
        f"check_secret_match = {common.IMPORT_NAME}.operations:check_secret_match",
    ]
}

setup(**common.KWARGS)
