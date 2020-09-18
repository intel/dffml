#!/usr/bin/env bash
#
# This file is responsible for installing any dependencies needed by the various
# DFFML plugins, the docs, and DFFML itself.

# set -e to exit this script if any programs run by this script fail
# set -x to echo everything we do before we do it
set -ex

CONDA_INSTALL_LOCATION="${1}"

if [ "x${CONDA_INSTALL_LOCATION}" != "x" ]; then
  mkdir -p "${CONDA_INSTALL_LOCATION}"
fi

# Get the python version in the format of pyMajorMinor, example: py37
python_version="py$(python -c 'import sys; print(f"{sys.version_info.major}{sys.version_info.minor}")')"

export PATH="${CONDA_INSTALL_LOCATION}/miniconda${python_version}/bin:$PATH"

# True or False for if `conda` is in the PATH
has_conda=$(python -c 'import pathlib, os; print(any(map(lambda path: pathlib.Path(path, "conda").is_file(), os.environ.get("PATH", "").split(":"))))')


# ========================== BEGIN GLOBAL DEPENDENCIES =========================
#
# Dependencies that are applicable to the main package and plugins, or just must
# be installed first.

# Install conda because some plugins have dependencies which are only available
# on conda (those listed first). Also because we need to install those packages
# for the integration tests for the main package (.) and when generating the
# docs. Has to be installed first because other packages will be installed into
# the environment that we set up using it (essentially a virtualenv)

# model/daal4py
# model/vowpalWabbit
# .
# docs
if [[ "${has_conda}" != "True" ]]; then
  # URL of conda
  conda_url="https://repo.anaconda.com/miniconda/Miniconda3-${python_version}_4.8.2-Linux-x86_64.sh"
  # Location to download conda to
  conda_download="${CONDA_INSTALL_LOCATION}/conda${python_version}.sh"
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
  bash "${conda_download}" -b -p "${CONDA_INSTALL_LOCATION}/miniconda${python_version}"
  # Update
  conda update -y -n base -c defaults conda
  # Add channels
  conda config --add channels anaconda
  conda config --add channels conda-forge
  # Remove numpy 1.19.1 see https://github.com/intel/dffml/issues/816
  # conda uninstall numpy
  # conda install numpy==1.18.5
  # For some reason conda doesn't come with pip?
  # Commit message: Update to 20.2.3
  GET_PIP_URL="https://github.com/pypa/get-pip/raw/fa7dc83944936bf09a0e4cb5d5ec852c0d256599/get-pip.py"
  PIP_HASH='b8bbf0ef2f8728c1337818cba5d48e8f2a7d18fbbe2ce253299306b5f79011b0365c3cf8852cdef0935e203d8aba6fba'
  GET_PIP_FILE="${CONDA_INSTALL_LOCATION}/get-pip.py"
  curl -L "${GET_PIP_URL}" -o "${GET_PIP_FILE}"
  sha384sum "${GET_PIP_FILE}" | grep "^${PIP_HASH}"
  python "${GET_PIP_FILE}"
  python -m pip install -U pip
fi
if [ -f "${CONDA_INSTALL_LOCATION}/miniconda${python_version}/bin/activate" ]; then
  source "${CONDA_INSTALL_LOCATION}/miniconda${python_version}/bin/activate" base
fi
