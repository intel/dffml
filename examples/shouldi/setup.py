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
    "console_scripts": ["shouldi = shouldi.cli:ShouldI.main"],
    "dffml.operation": [
        "run_bandit = shouldi.python.bandit:run_bandit",
        "safety_check = shouldi.python.safety:safety_check",
        "pypi_package_json = shouldi.python.pypi:pypi_package_json",
        "pypi_package_contents = shouldi.python.pypi:pypi_package_contents",
        "cleanup_pypi_package = shouldi.python.pypi:cleanup_pypi_package",
    ],
}

setup(**common.KWARGS)
