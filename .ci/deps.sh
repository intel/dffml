#!/usr/bin/env bash
set -ex

export PLUGIN="${1}"

if [ "x${PIP_CACHE_DIR}" != "x" ]; then
  mkdir -p "${PIP_CACHE_DIR}"
fi

python_version="py$(python -c 'import sys; print(f"{sys.version_info.major}{sys.version_info.minor}")')"

export PATH="${PIP_CACHE_DIR}/miniconda${python_version}/bin:$PATH"

has_conda=$(python -c 'import pathlib, os; print(any(map(lambda path: pathlib.Path(path, "conda").is_file(), os.environ.get("PATH", "").split(":"))))')

mkdir -p "${HOME}/.local/bin"

if [[ "x${PLUGIN}" == "xmodel/vowpalWabbit" ]] || [[ "x${PLUGIN}" == "x." ]] || [[ "x${PLUGIN}" == "xdocs" ]]; then
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

python -m pip install --upgrade pip setuptools twine

# Install main package
pip install -U -e .[dev]

if [ "${PLUGIN}" == "feature/git" ]; then
  curl -sSL https://github.com/XAMPPRocky/tokei/releases/download/v9.1.1/tokei-v9.1.1-x86_64-unknown-linux-gnu.tar.gz | tar xvz -C "$HOME/.local/bin/"
  sudo apt-get update && sudo apt-get install -y git subversion cloc openssl
fi

if [ "${PLUGIN}" == "source/mysql" ]; then
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
  sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
  sudo apt-get update && sudo apt-get install -y docker-ce docker-ce-cli containerd.io
  docker pull mariadb:10
fi

if [[ "x${PLUGIN}" == "xmodel/vowpalWabbit" ]] || [[ "x${PLUGIN}" == "x." ]] || [[ "x${PLUGIN}" == "xdocs" ]]; then
  conda install -y -c conda-forge vowpalwabbit
fi

if [ "x${PLUGIN}" == "xmodel/tensorflow_hub" ]; then
  python -m pip install -U -e "./model/tensorflow"
fi
