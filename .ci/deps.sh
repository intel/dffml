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

export PATH="${PIP_CACHE_DIR}/miniconda${python_version}/bin:$PATH"

# True or False for if `conda` is in the PATH
has_conda=$(python -c 'import pathlib, os; print(any(map(lambda path: pathlib.Path(path, "conda").is_file(), os.environ.get("PATH", "").split(":"))))')

mkdir -p "${HOME}/.local/bin"


# ========================== BEGIN GLOBAL DEPENDENCIES =========================
#
# Dependencies that are applicable to the main package and plugins, or just must
# be installed first.

# Install conda because some plugins have dependencies which are only available
# on conda (those listed first). Also because we need to install those packages
# for the integration tests for the main package (.) and when generating the
# docs. Has to be installed first because other packages will be installed into
# the environment that we set up using it (essentially a virtualenv)
if [[ "x${PLUGIN}" == "xmodel/daal4py" ]] || \
   [[ "x${PLUGIN}" == "xmodel/vowpalWabbit" ]] || \
   [[ "x${PLUGIN}" == "x." ]] || \
   [[ "x${PLUGIN}" == "xdocs" ]]; then
  if [[ "${has_conda}" != "True" ]]; then
    # URL of conda
    conda_url="https://repo.anaconda.com/miniconda/Miniconda3-${python_version}_4.8.2-Linux-x86_64.sh"
    # Location to download conda to
    conda_download="${PIP_CACHE_DIR}/conda${python_version}.sh"
    # Hash of conda download
    if [ "${python_version}" == "py37" ]; then
      conda_hash=957d2f0f0701c3d1335e3b39f235d197837ad69a944fa6f5d8ad2c686b69df3b
    elif [ "${python_version}" == "py38" ]; then
      conda_hash=5bbb193fd201ebe25f4aeb3c58ba83feced6a25982ef4afa86d5506c3656c142
    fi
    # Download it
    if [ ! -f "${conda_download}" ]; then
      curl -L "${conda_url}" -o "${conda_download}"
    fi
    # Verify the hash
    sha256sum "${conda_download}" | grep "^${conda_hash}"
    # Run it
    bash "${conda_download}" -b -p "${PIP_CACHE_DIR}/miniconda${python_version}"
    # Update
    conda update -y -n base -c defaults conda
    # Add channels
    conda config --add channels anaconda
    conda config --add channels conda-forge
  fi
  if [ -f "${PIP_CACHE_DIR}/miniconda${python_version}/bin/activate" ]; then
    source "${PIP_CACHE_DIR}/miniconda${python_version}/bin/activate" base
  fi
fi

# Install and upgrade
# pip and setuptools, which are used to install other packages
# twine, which is used to upload released packages to PyPi
python -m pip install --upgrade pip setuptools twine

# Install main package so that other packages have access to it
python -m pip install -U -e .[dev]

# ==========================  END  GLOBAL DEPENDENCIES =========================


# =========================== BEGIN TEST DEPENDENCIES ==========================
#
# Dependencies for specific plugins only used when running the tests for those
# plugins. Not when generating docs or running main package integration tests

if [[ "x${PLUGIN}" == "xfeature/git" ]] || \
   [[ "x${PLUGIN}" == "xoperations/deploy" ]]; then
  curl -sSL https://github.com/XAMPPRocky/tokei/releases/download/v9.1.1/tokei-v9.1.1-x86_64-unknown-linux-gnu.tar.gz | tar xvz -C "$HOME/.local/bin/"
  sudo apt-get update && sudo apt-get install -y git subversion cloc openssl
fi

if [ "${PLUGIN}" == "source/mysql" ]; then
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

if [[ "x${PLUGIN}" == "xmodel/vowpalWabbit" ]] || \
   [[ "x${PLUGIN}" == "x." ]] || \
   [[ "x${PLUGIN}" == "xdocs" ]]; then
  set +e
  # conda sometimes is a bash function, which does not abide by strict error
  # checking, so we have to turn off exit on error and only exit if the return
  # code of the conda bash function is non-zero
  conda install -y -c conda-forge vowpalwabbit
  exit_code=$?
  if [[ "x${exit_code}" != "x0" ]]; then
    exit "${exit_code}"
  fi
  set -e
fi

if ([[ "x${PLUGIN}" == "xmodel/daal4py" ]] || \
    [[ "x${PLUGIN}" == "x." ]] || \
    [[ "x${PLUGIN}" == "xdocs" ]]) &&
  [[ "${python_version}" != "py38" ]]; then
  # daal4py only supports ^ Python 3.7
  set +e
  # See comment in vowpalWabbit about conda exit codes
  conda install -y -c intel daal4py
  exit_code=$?
  if [[ "x${exit_code}" != "x0" ]]; then
    exit "${exit_code}"
  fi
  set -e
fi

if [[ "x${PLUGIN}" == "xoperations/nlp" ]]; then
  # See comment in vowpalWabbit about conda exit codes
  set +e
  conda install -y -c conda-forge spacy
  exit_code=$?
  if [[ "x${exit_code}" != "x0" ]]; then
    exit "${exit_code}"
  fi
  set -e
  python -m spacy download en_core_web_sm
fi

if [[ "x${PLUGIN}" == "xmodel/autosklearn" ]] || \
   [[ "x${PLUGIN}" == "x." ]] || \
   [[ "x${PLUGIN}" == "xdocs" ]]; then
  sudo apt-get install -y build-essential swig
  curl https://raw.githubusercontent.com/automl/auto-sklearn/master/requirements.txt |
    xargs -n 1 -L 1 pip install
fi

# ==========================  END  INSTALL DEPENDENCIES ========================


# =========================== BEGIN INTER DEPENDENCIES =========================
#
# Core plugins which depend on other code plugins should install those core
# plugins that they depend on here

if [ "x${PLUGIN}" == "xmodel/tensorflow_hub" ]; then
  python -m pip install -U -e "./model/tensorflow"
fi

if [[ "x${PLUGIN}" == "xoperations/deploy" ]]; then
  python -m pip install -U -e "./feature/git"
fi

if [[ "x${PLUGIN}" == "xoperations/nlp" ]]; then
  conda install -y -c conda-forge spacy
  python -m spacy download en_core_web_sm
  python -m pip install -U -e "./model/tensorflow"
fi

if [ "x${PLUGIN}" = "xexamples/shouldi" ]; then
  python -m pip install -U -e "./feature/git"
fi

# ===========================  END  INTER DEPENDENCIES =========================
