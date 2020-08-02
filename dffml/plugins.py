"""
This file is imported by the top level setup.py and therefore must remain as
independent as possible (no relative imports)
"""
import os
import sys
import pathlib
import inspect
import tempfile
import contextlib
import subprocess
import importlib.util


def inpath(binary):
    return any(
        list(
            map(
                lambda dirname: os.path.isfile(os.path.join(dirname, binary)),
                os.environ.get("PATH", "").split(":"),
            )
        )
    )


# List of plugins
CORE_PLUGINS = [
    ("configloader", "yaml"),
    ("configloader", "image"),
    ("model", "scratch"),
    ("model", "scikit"),
    ("model", "tensorflow"),
    ("model", "tensorflow_hub"),
    ("model", "transformers"),
    ("model", "vowpalWabbit"),
    ("model", "autosklearn"),
    ("model", "xgboost"),
    ("model", "pytorch"),
    ("model", "spacy"),
]

# Models which currently don't support Python 3.8
if sys.version_info.major == 3 and sys.version_info.minor < 8:
    CORE_PLUGINS += [
        ("model", "daal4py"),
    ]

CORE_PLUGINS += [
    ("examples", "shouldi"),
    ("feature", "git"),
    ("feature", "auth"),
    ("operations", "binsec"),
    ("operations", "deploy"),
    ("operations", "image"),
    ("operations", "nlp"),
    ("service", "http"),
    ("source", "mysql"),
]


def python_package_installed(module_name: str) -> bool:
    """
    Check if a Python package is installed and can be imported
    """
    spec = None
    with contextlib.suppress(ModuleNotFoundError):
        spec = importlib.util.find_spec(module_name)
    return bool(spec is not None)


# Dependencies of plugins and how to check if they exist on the system or not


def check_boost():
    # TODO Implement check on Windows
    if os.name == "nt":
        return True
    with tempfile.TemporaryDirectory() as tempdir:
        c_file = pathlib.Path(tempdir, "main.c")
        c_file.write_text(
            inspect.cleandoc(
                r"""
            #include <boost/version.hpp>

            int main() {
                return 0;
            }
            """
            )
        )
        return bool(
            subprocess.call(
                ["c++", str(c_file)],
                cwd=tempdir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            == 0
        )


CORE_PLUGIN_DEPS = {
    ("model", "vowpalWabbit"): {
        "cmake": lambda: inpath("cmake"),
        "boost": check_boost,
    }
    if not python_package_installed("vowpalwabbit")
    else {},
    ("model", "autosklearn"): {
        "swig": lambda: inpath("swig"),
        "cython": lambda: inpath("cython"),
    }
    if not python_package_installed("auto_sklearn")
    else {},
}

# Plugins which currently don't support Python 3.8
if sys.version_info.major == 3 and sys.version_info.minor < 8:
    CORE_PLUGIN_DEPS[("model", "daal4py")] = {
        # Must be installed already via conda, do not provide a pypi package yet
        "daal4py": lambda: python_package_installed("daal4py")
    }

# All packages under configloader/ are really named dffml-config-{name}
ALTERNATIVES = {"configloader": "config"}

# Build a dict of plugin_type_name (aka model, config): list(package_names)
def package_names_by_plugin(validation=None):
    by_plugin = {
        (plugin_type + ("s" if not plugin_type.endswith("s") else "")): [
            "dffml-%s-%s"
            % (
                ALTERNATIVES.get(plugin_type, plugin_type),
                name.replace("_", "-"),
            )
            for sub_plugin_type, name in CORE_PLUGINS
            if sub_plugin_type == plugin_type
            and (not validation or validation(sub_plugin_type, name))
        ]
        for plugin_type, plugin_name in CORE_PLUGINS
        if plugin_type != "examples"
    }
    # Operations used to be named features
    by_plugin["operations"].extend(by_plugin["features"])
    del by_plugin["features"]

    # All packages
    by_plugin["all"] = [
        "dffml-%s-%s"
        % (ALTERNATIVES.get(plugin_type, plugin_type), name.replace("_", "-"),)
        for plugin_type, name in CORE_PLUGINS
        if plugin_type != "examples"
        and (not validation or validation(plugin_type, name))
    ]

    return by_plugin


PACKAGE_NAMES_BY_PLUGIN = package_names_by_plugin()

# Same as PACKAGE_NAMES_BY_PLUGIN but only with plugins that have all their
# pre-install dependencies met
PACKAGE_NAMES_BY_PLUGIN_INSTALLABLE = package_names_by_plugin(
    lambda plugin_type, plugin_name: all(
        map(
            lambda check: check(),
            CORE_PLUGIN_DEPS.get((plugin_type, plugin_name), {}).values(),
        )
    )
)
