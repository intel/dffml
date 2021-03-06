# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import pathlib
import datetime
import subprocess

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "_ext"))
)

from dffml.version import VERSION

# -- Project information -----------------------------------------------------

project = "DFFML"
copyright = "2017 - %d, Intel" % (datetime.datetime.today().year,)
author = "John Andersen"

# The short X.Y version
version = VERSION

if pathlib.Path(__file__).parent.parent.joinpath(".git").is_dir():
    git_show_output = (
        subprocess.check_output(
            ["git", "show", "-s", "--pretty=%h %D", "HEAD"]
        )
        .decode()
        .split()
    )
    if "tag:" not in git_show_output:
        version = git_show_output[0]

# The full version, including alpha/beta/rc tags
release = version


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.intersphinx",
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx_tabs.tabs",
    "recommonmark",
    "dffml.util.testing.consoletest.builder",
    "literalinclude_diff",
    "literalinclude_relative",
]

intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# Enable markdown
source_suffix = {
    ".rst": "restructuredtext",
    ".txt": "markdown",
    ".md": "markdown",
}


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

html_context = {
    "github_user": "intel",
    "github_repo": "dffml",
    "github_version": "master",
    "conf_py_path": "/docs/",
    "display_github": True,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]


def setup(app):
    app.add_js_file("copybutton.js")


# -- Extension configuration -------------------------------------------------

napoleon_numpy_docstring = True

consoletest_root = os.path.abspath("..")
consoletest_docs = os.path.join(consoletest_root, "docs")
consoletest_test_setup = (
    pathlib.Path(__file__).parent / "consoletest_test_setup.py"
).read_text()
