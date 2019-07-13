import os
import ast
from io import open
from setuptools import find_packages, setup

ORG = "nucleon"
NAME = "scikit"
DESCRIPTION = "DFFML model scikit"
AUTHOR_NAME = "Yash Lamba"
AUTHOR_EMAIL = "yashlamba2000@gmail.com"
INSTALL_REQUIRES = ["dffml>=0.2.1"]

IMPORT_NAME = (
    NAME
    if "replace_package_name".upper() != NAME
    else "replace_import_package_name".upper()
).replace("-", "_")

SELF_PATH = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(SELF_PATH, IMPORT_NAME, "version.py"), "r") as f:
    for line in f:
        if line.startswith("VERSION"):
            version = ast.literal_eval(line.strip().split("=")[-1].strip())
            break

with open(os.path.join(SELF_PATH, "README.md"), "r", encoding="utf-8") as f:
    readme = f.read()

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
    url=f"https://github.com/{ORG}/{NAME}",
    license="MIT",
    keywords=["dffml"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    install_requires=INSTALL_REQUIRES,
    packages=find_packages(),
    entry_points={"dffml.model": [f"misc = {IMPORT_NAME}.misc:Misc"]},
)
