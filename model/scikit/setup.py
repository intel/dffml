import os
import sys
import ast
from io import open
from setuptools import find_packages, setup

ORG = "intel"
NAME = "dffml-model-scikit"
DESCRIPTION = "DFFML model scikit"
AUTHOR_NAME = "Yash Lamba"
AUTHOR_EMAIL = "yashlamba2000@gmail.com"
INSTALL_REQUIRES = [
    "scikit-learn>=0.21.2",
    "joblib>=0.13.2",
    "pandas>=0.25.0",
] + (
    ["dffml>=0.3.0"]
    if not any(
        list(
            map(
                os.path.isfile,
                list(
                    map(
                        lambda syspath: os.path.join(
                            syspath, "dffml.egg-link"
                        ),
                        sys.path,
                    )
                ),
            )
        )
    )
    else []
)

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
    name="dffml-model-scikit",
    version=version,
    description="",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Yash Lamba",
    author_email="yashlamba2000@gmail.com",
    maintainer="John Andersen",
    maintainer_email="john.s.andersen@intel.com",
    url="https://github.com/intel/dffml/blob/master/model/scikit/README.md",
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
    entry_points={
        "dffml.model": [
            f"scikitknn = {IMPORT_NAME}.scikit_models:KNeighborsClassifierModel",
            f"scikitadaboost = {IMPORT_NAME}.scikit_models:AdaBoostClassifierModel",
            f"scikitgpc = {IMPORT_NAME}.scikit_models:GaussianProcessClassifierModel",
            f"scikitdtc = {IMPORT_NAME}.scikit_models:DecisionTreeClassifierModel",
            f"scikitrfc = {IMPORT_NAME}.scikit_models:RandomForestClassifierModel",
            f"scikitmlp = {IMPORT_NAME}.scikit_models:MLPClassifierModel",
            f"scikitgnb = {IMPORT_NAME}.scikit_models:GaussianNBModel",
            f"scikitqda = {IMPORT_NAME}.scikit_models:QuadraticDiscriminantAnalysisModel",
            f"scikitsvc = {IMPORT_NAME}.scikit_models:SVCModel",
            f"scikitlr = {IMPORT_NAME}.scikit_models:LinearRegressionModel",
        ]
    },
)
