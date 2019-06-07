import os
import ast
from io import open

from setuptools import find_packages, setup

self_path = os.path.dirname(os.path.realpath(__file__))

NAME = "shouldi"
AUTHOR_NAME = "John Andersen"
AUTHOR_EMAIL = "john.s.andersen@intel.com"
DESCRIPTION = "Meta static analysis runner for Python packages"

with open(os.path.join(self_path, NAME, "version.py"), "r") as f:
    for line in f:
        if line.startswith("VERSION"):
            version = ast.literal_eval(line.strip().split("=")[-1].strip())
            break

with open(os.path.join(self_path, "README.md"), "r", encoding="utf-8") as f:
    readme = f.read()

INSTALL_REQUIRES = ["aiohttp>=3.5.4", "dffml>=0.2.1"]

setup(
    name=NAME,
    version=version,
    description=DESCRIPTION,
    long_description=readme,
    long_description_content_type="text/markdown",
    author=AUTHOR_NAME,
    author_email=AUTHOR_EMAIL,
    maintainer=AUTHOR_NAME,
    maintainer_email=AUTHOR_EMAIL,
    url="https://github.com/intel/dffml/blob/master/examples/shouldi/README.md",
    license="MIT",
    keywords=[""],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    install_requires=INSTALL_REQUIRES,
    tests_require=[],
    packages=find_packages(),
    entry_points={"console_scripts": ["shouldi = shouldi.cli:ShouldI.main"]},
)
