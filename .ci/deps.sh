#!/usr/bin/env bash
#
# This file is responsible for installing any dependencies needed by the various
# DFFML plugins, the docs, and DFFML itself.

# set -e to exit this script if any programs run by this script fail
# set -x to echo everything we do before we do it
set -ex

export PLUGIN="${1}"

if [ "x${PIP_CACHE_DIR}" != "x" ]; then
  mkdir -p "${PIP_CACHE_DIR}"
fi

# Get the python version in the format of pyMajorMinor, example: py37
python_version="py$(python -c 'import sys; print(f"{sys.version_info.major}{sys.version_info.minor}")')"

mkdir -p "${HOME}/.local/bin"


# ========================== BEGIN GLOBAL DEPENDENCIES =========================
#
# Dependencies that are applicable to the main package and plugins, or just must
# be installed first.

# Install and upgrade
# pip and setuptools, which are used to install other packages
# twine, which is used to upload released packages to PyPi
python -m pip install --upgrade pip setuptools wheel twine

# Install main package so that other packages have access to it
python -m pip install -U -e .[dev]

# ==========================  END  GLOBAL DEPENDENCIES =========================


# =========================== BEGIN TEST DEPENDENCIES ==========================
#
# Dependencies for specific plugins only used when running the tests for those
# plugins. Used when running main package consoletests on the documentation. Not
# when generating html docs.

if [[ "x${PLUGIN}" == "xfeature/git" ]] || \
   [[ "x${PLUGIN}" == "xoperations/deploy" ]] || \
   [[ "x${PLUGIN}" == "x." ]]; then
  curl -sSL https://github.com/XAMPPRocky/tokei/releases/download/v9.1.1/tokei-v9.1.1-x86_64-unknown-linux-gnu.tar.gz | tar xvz -C "$HOME/.local/bin/"
  sudo apt-get update && sudo apt-get install -y git subversion cloc openssl
fi

if [[ "x${PLUGIN}" == "xsource/mysql" ]] || \
   [[ "x${PLUGIN}" == "x." ]]; then
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
  sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
  sudo apt-get update && sudo apt-get install -y docker-ce docker-ce-cli containerd.io
  docker pull mariadb:10
fi

# ===========================  END  TEST DEPENDENCIES ==========================


# ========================== BEGIN INSTALL DEPENDENCIES ========================
#
# Dependencies which must be installed prior to installing a plugin. If a plugin
# requires something be installed, it must also ensure that those dependencies
# get installed when we are running the tests for the main package (.) or the
# docs (docs). Each if statement seen here will check if we are running tests
# for the plugin, main package, or docs, and install if any of those conditions
# are true.

if [[ "x${PLUGIN}" == "xmodel/autosklearn" ]] || \
   [[ "x${PLUGIN}" == "x." ]] || \
   [[ "x${PLUGIN}" == "xdocs" ]]; then
  sudo apt-get install -y build-essential swig
  python -m pip install cython
  curl -L 'https://github.com/automl/auto-sklearn/raw/2786d636e92507323b21be7692fbbf8b3f37f7f3/requirements.txt' |
    xargs -n 1 -L 1 python -m pip install
  python -m pip install liac-arff psutil smac==0.12.3
fi

# ==========================  END  INSTALL DEPENDENCIES ========================


# =========================== BEGIN INTER DEPENDENCIES =========================
#
# Core plugins which depend on other code plugins should install those core
# plugins that they depend on here

if [ "x${PLUGIN}" == "xmodel/tensorflow_hub" ]; then
  python -m pip install -U -e "./model/tensorflow"
fi

if [[ "x${PLUGIN}" == "xmodel/spacy" ]]; then
  python -m pip install spacy
  python -m spacy download en_core_web_sm
fi

if [[ "x${PLUGIN}" == "xoperations/deploy" ]]; then
  python -m pip install -U -e "./feature/git"
fi

if [[ "x${PLUGIN}" == "xoperations/nlp" ]]; then
  python -m pip install spacy
  python -m spacy download en_core_web_sm
  python -m pip install -U -e "./model/tensorflow"
fi

if [ "x${PLUGIN}" = "xexamples/shouldi" ]; then
  python -m pip install -U -e "./feature/git"
fi

# ===========================  END  INTER DEPENDENCIES =========================
