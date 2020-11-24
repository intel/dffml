FROM python:3.7-buster

# ========================== BEGIN DOCKER SETUP ================================
#
# Docker related setup

# Tell apt that we can't answer it's questions if it has any (time zone is a
# common one)
ENV DEBIAN_FRONTEND noninteractive

# The version of python we're using in pyXY format (changes with base image)
ARG PYTHON_SHORT_VERSION=py37
ENV PYTHON_SHORT_VERSION ${PYTHON_SHORT_VERSION}

# The location we should install conda to
ARG CONDA_INSTALL_LOCATION=/opt/conda
ENV CONDA_INSTALL_LOCATION ${CONDA_INSTALL_LOCATION}

# Set current working directory
WORKDIR /usr/src/dffml

# ==========================  END  DOCKER SETUP ================================


# ========================== BEGIN GLOBAL DEPENDENCIES =========================
#
# Dependencies that are applicable to the main package and plugins, or just must
# be installed first.

# Copy over conda install script
COPY .ci/conda.sh .ci/conda.sh
# Install conda because some plugins have dependencies which are only available
# on conda (those listed first). Also because we need to install those packages
# for the integration tests for the main package (.) and when generating the
# docs. Has to be installed first because other packages will be installed into
# the environment that we set up using it (essentially a virtualenv)
RUN .ci/conda.sh ${CONDA_INSTALL_LOCATION}
# Install and upgrade
# pip and setuptools, which are used to install other packages
# twine, which is used to upload released packages to PyPi
RUN python -m pip install --upgrade pip setuptools twine

# ==========================  END  GLOBAL DEPENDENCIES =========================


# ====================== BEGIN NON PYTHON DEPENDENCIES =========================
#
# Dependencies for specific plugins that cannot be installed with pip or conda

# feature/git
# operations/deploy
RUN curl -o /tmp/tokei.tar.gz -L 'https://github.com/XAMPPRocky/tokei/releases/download/v12.0.4/tokei-x86_64-unknown-linux-gnu.tar.gz' && \
  sha384sum /tmp/tokei.tar.gz | grep "^60ea048eca4d5e9f413400a561c775ccd21ffb63e3d15cc60703156bd634eb4c3ddec3bd8e8b8aabdaf97bb9b8d0ec11" && \
  tar xvzf /tmp/tokei.tar.gz -C "/usr/bin/" && \
  rm /tmp/tokei.tar.gz && \
  apt-get update && \
  apt-get install -y \
    git \
    subversion \
    cloc \
    openssl && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

# ======================  END  NON PYTHON DEPENDENCIES =========================


# ========================== BEGIN INSTALL DEPENDENCIES ========================
#
# Dependencies which must be installed prior to installing a plugin. If a plugin
# requires something be installed, it must also ensure that those dependencies
# get installed when we are running the tests for the main package (.) or the
# docs (docs). Each if statement seen here will check if we are running tests
# for the plugin, main package, or docs, and install if any of those conditions
# are true.

# model/vowpalWabbit
# .
# docs
RUN . "${CONDA_INSTALL_LOCATION}/miniconda${PYTHON_SHORT_VERSION}/bin/activate" base && \
  conda install -y -c conda-forge vowpalwabbit

# model/daal4py
# .
# docs
RUN . "${CONDA_INSTALL_LOCATION}/miniconda${PYTHON_SHORT_VERSION}/bin/activate" base && \
  if [ "x${PYTHON_SHORT_VERSION}" != "xpy38" ]; then conda install -y -c intel daal4py==2020.1 daal==2020.1; fi

# operations/nlp
RUN . "${CONDA_INSTALL_LOCATION}/miniconda${PYTHON_SHORT_VERSION}/bin/activate" base && \
  conda install -y -c conda-forge spacy && \
  python -m spacy download en_core_web_sm

# model/autosklearn
# .
# docs
RUN . "${CONDA_INSTALL_LOCATION}/miniconda${PYTHON_SHORT_VERSION}/bin/activate" base && \
  apt-get update && \
  apt-get install -y \
    build-essential \
    swig && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* && \
  python -m pip install pyrfr cython liac-arff

# ==========================  END  INSTALL DEPENDENCIES ========================


# ========================== BEGIN INSTALL DEPENDENCIES ========================
#
# Here we install DFFML and all the plugins

# The release of dffml we're using, latest is the latest PyPi release, master is
# the master branch
ARG DFFML_RELEASE=latest
ENV DFFML_RELEASE ${DFFML_RELEASE}

# Copy over DFFML
COPY . /usr/src/dffml
# Install the correct version of DFFML
RUN /usr/src/dffml/.ci/dffml-install.sh

# Copy over entrypoint script
COPY scripts/docker-entrypoint.sh /usr/bin/docker-entrypoint.sh

ENTRYPOINT /usr/bin/docker-entrypoint.sh
