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
author = "DFFML Authors"

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
    "nbsphinx",
    "nbsphinx_link",
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

# Download button for ipython notebooks
# This is processed by Jinja2 and inserted before each notebook
nbsphinx_prolog = r"""
{% set docname = env.doc2path(env.docname, base=None) %}
{% if "." not in env.config.release %}
    {% set nb_version = "main/" %}
{% endif %}

.. image:: https://dffml.github.io/dffml-pre-image-removal/master/_images/Download-.ipynb-button.svg
    :target: https://intel.github.io/dffml/{{ nb_version }}{{ docname[:-6] }}ipynb
    :alt: Notebook download button

|
"""

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

html_context = {
    "github_user": "intel",
    "github_repo": "dffml",
    "github_version": "main",
    "conf_py_path": "/docs/",
    "display_github": True,
}


def setup(app):
    app.add_js_file("copybutton.js")


# -- Extension configuration -------------------------------------------------

napoleon_numpy_docstring = True

consoletest_root = os.path.abspath("..")
consoletest_docs = os.path.join(consoletest_root, "docs")
consoletest_test_setup = (
    pathlib.Path(__file__).parent / "consoletest_test_setup.py"
).read_text()
