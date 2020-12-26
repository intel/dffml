import os
import sys
import ast
from pathlib import Path
from io import open

from setuptools import find_packages, setup

self_path = os.path.dirname(os.path.realpath(__file__))

with open(
    os.path.join(self_path, "dffml_operations_binsec", "version.py"), "r"
) as f:
    for line in f:
        if line.startswith("VERSION"):
            version = ast.literal_eval(line.strip().split("=")[-1].strip())
            break

with open(os.path.join(self_path, "README.md"), "r", encoding="utf-8") as f:
    readme = f.read()

INSTALL_REQUIRES = [] + (
    ["dffml>=0.3.7"]
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

REQUIREMENTS_TXT_PATH = Path(self_path, "requirements.txt")
if REQUIREMENTS_TXT_PATH.is_file():
    INSTALL_REQUIRES += list(
        map(lambda i: i.strip(), REQUIREMENTS_TXT_PATH.read_text().split("\n"))
    )

setup(
    name="dffml_operations_binsec",
    version=version,
    description="",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Himanshu Tripathi",
    author_email="himanshutripathi366@gmail.com",
    url="https://github.com/intel/dffml/blob/master/operations/binsec/README.md",
    license="MIT",
    keywords=[""],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "License :: OSI Approved :: Apache Software License",
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
        "dffml.operation": [
            "url_to_urlbytes = dffml_operations_binsec.operations:URLToURLBytes",
            "urlbytes_to_tarfile = dffml_operations_binsec.operations:urlbytes_to_tarfile",
            "urlbytes_to_rpmfile = dffml_operations_binsec.operations:urlbytes_to_rpmfile",
            "files_in_rpm = dffml_operations_binsec.operations:files_in_rpm",
            "is_binary_pie = dffml_operations_binsec.operations:is_binary_pie",
            "cleanup_rpm = dffml_operations_binsec.operations:cleanup_rpm",
        ]
    },
)
