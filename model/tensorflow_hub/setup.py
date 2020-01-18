# import os
# import importlib.util
# from setuptools import setup

# # Boilerplate to load commonalities
# spec = importlib.util.spec_from_file_location(
#     "setup_common", os.path.join(os.path.dirname(__file__), "setup_common.py")
# )
# common = importlib.util.module_from_spec(spec)
# spec.loader.exec_module(common)

# common.KWARGS["entry_points"] = {
#     "dffml.model": [f"misc = {common.IMPORT_NAME}.misc:MiscModel"]
# }

# setup(**common.KWARGS)
import os
import sys
import ast
from io import open

from setuptools import find_packages, setup

self_path = os.path.dirname(os.path.realpath(__file__))

with open(
    os.path.join(self_path, "dffml_model_tensorflow_hub", "version.py"), "r"
) as f:
    for line in f:
        if line.startswith("VERSION"):
            version = ast.literal_eval(line.strip().split("=")[-1].strip())
            break

with open(os.path.join(self_path, "README.md"), "r", encoding="utf-8") as f:
    readme = f.read()

INSTALL_REQUIRES = ["tensorflow>=2.0.0b", "tensorflow-hub>=0.3"] + (
    ["dffml>=0.3.1"]
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

setup(
    name="dffml-model-tensorflow-hub",
    version=version,
    description="",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Himanshu Tripathi",
    author_email="himanshutripathi366@gmail.com",
    url="https://github.com/intel/dffml/blob/master/model/tensorflow_hub/README.md",
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
        "dffml.model": [
            "text_classifier = dffml_model_tensorflow_hub.text_classifier:TextClassificationModel",
            # "tfdnnr = dffml_model_tensorflow.dnnr:DNNRegressionModel",
        ]
    },
)
