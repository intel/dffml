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
import datetime

try:
    from importlib.metadata import version as importlib_metadata_version
except (ImportError, ModuleNotFoundError):
    from importlib_metadata import version as importlib_metadata_version

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
# sys.path.append(
#     os.path.abspath(os.path.join(os.path.dirname(__file__), "_ext"))
# )

# -- Project information -----------------------------------------------------

project = "REPLACE_PACKAGE_NAME"
author = project + " Authors"
copyright = "2021 - %d, %s" % (datetime.datetime.today().year, author)

# The short X.Y version
version = importlib_metadata_version("REPLACE_PACKAGE_NAME")
# The full version, including alpha/beta/rc tags
release = version


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.intersphinx",
    "sphinx.ext.autodoc",
]

intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "alabaster"
