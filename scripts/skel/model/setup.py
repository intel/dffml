import os
import ast
from io import open

from setuptools import find_packages, setup

self_path = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(self_path, 'dffml_model_model_name', 'version.py'),
          'r') as f:
    for line in f:
        if line.startswith('VERSION'):
            version = ast.literal_eval(line.strip().split('=')[-1].strip())
            break

with open(os.path.join(self_path, 'README.md'), 'r', encoding='utf-8') as f:
    readme = f.read()

INSTALL_REQUIRES = [
    ]

setup(
    name='dffml-model-model_name',
    version=version,
    description='',
    long_description=readme,
    author='John Andersen',
    author_email='john.s.andersen@intel.com',
    url='https://github.com/intel/dffml/blob/master/model/model_name/README.md',
    license='MIT',

    keywords=[
        '',
    ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],

    install_requires=INSTALL_REQUIRES,

    packages=find_packages(),
    entry_points={
        'dffml.model': [
            'dnn = dffml_model_model_name.model.misc:Misc',
        ],
    },
)
