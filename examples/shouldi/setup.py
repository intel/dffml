import os
import importlib.util
from setuptools import setup

# Boilerplate to load commonalities
spec = importlib.util.spec_from_file_location(
    "setup_common", os.path.join(os.path.dirname(__file__), "setup_common.py")
)
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)

common.KWARGS["install_requires"] += [
    "aiohttp>=3.5.4",
    "bandit>=1.6.2",
    "safety>=1.8.5",
]
common.KWARGS["entry_points"] = {
    "console_scripts": ["shouldi = shouldi.cli:ShouldI.main"],
    "dffml.operation": [
        "run_bandit = shouldi.python.bandit:run_bandit",
        "safety_check = shouldi.python.safety:safety_check",
        "pypi_latest_package_version = shouldi.python.pypi:pypi_latest_package_version",
        "pypi_package_json = shouldi.python.pypi:pypi_package_json",
        "pypi_package_url = shouldi.python.pypi:pypi_package_url",
        "pypi_package_contents = shouldi.python.pypi:pypi_package_contents",
        "cleanup_pypi_package = shouldi.python.pypi:cleanup_pypi_package",
    ],
}

# Hiding down hear away from operations tutorial
common.KWARGS["install_requires"] += [
    "PyYAML>=5.1.2",
]
common.KWARGS["entry_points"].update(
    {
        "shouldi.project.bom.db": [
            "yaml = shouldi.project.bom.db.yaml:YAMLDB",
            "pypi = shouldi.project.bom.db.pypi:PyPiDB",
        ]
    }
)

setup(**common.KWARGS)
