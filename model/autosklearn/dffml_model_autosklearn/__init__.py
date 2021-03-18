"""
.. warning:

    auto-sklearn introduces a GPLv3 transitive dependency, ``lazy_import``!
    See
    https://softwareengineering.stackexchange.com/questions/323500/open-source-transitive-dependency-licenses
    for more information

Follow these instructions before running the above install
command to ensure that ``auto-sklearn`` installs correctly

**Ubuntu Installation**

To provide a C++11 building environment and the lateste SWIG version on Ubuntu, run:

.. code-block:: console

    $ sudo apt-get install build-essential swig

Install other PyPi dependencies with

.. code-block:: console

    $ python3 -m pip install cython liac-arff psutil
    $ curl https://raw.githubusercontent.com/automl/auto-sklearn/master/requirements.txt | xargs -n 1 -L 1 python3 -m pip install

For more information about installation visit https://automl.github.io/auto-sklearn/master/installation.html#installation
"""

from .autoregressor import AutoSklearnRegressorModel
from .autoclassifier import AutoSklearnClassifierModel
