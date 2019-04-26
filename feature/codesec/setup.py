import os
import ast
from io import open

from setuptools import find_packages, setup

self_path = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(self_path, 'dffml_feature_codesec', 'version.py'),
          'r') as f:
    for line in f:
        if line.startswith('VERSION'):
            version = ast.literal_eval(line.strip().split('=')[-1].strip())
            break

with open(os.path.join(self_path, 'README.md'), 'r', encoding='utf-8') as f:
    readme = f.read()

INSTALL_REQUIRES = [
    'aiohttp>=3.5.4',
    # 'rpmfile>=1.0.0',
    'pyelftools>=0.25',
    ]

setup(
    name='dffml_feature_codesec',
    version=version,
    description='',
    long_description=readme,
    author='John Andersen',
    author_email='john.s.andersen@intel.com',
    url='https://github.com/intel/dffml/blob/master/feature/codesec/README.md',
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
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],

    install_requires=INSTALL_REQUIRES,
    tests_require=[],

    packages=find_packages(),
    entry_points={
        'dffml.operation': [
            'rpm_url_to_rpmfile = dffml_feature_codesec.feature.operations:rpm_url_to_rpmfile',
            'files_in_rpm = dffml_feature_codesec.feature.operations:files_in_rpm.op',
            'binary_file = dffml_feature_codesec.feature.operations:binary_file.op',
            'pwn_checksec = dffml_feature_codesec.feature.operations:pwn_checksec.op',
            'cleanup_rpm = dffml_feature_codesec.feature.operations:cleanup_rpm.op',
            'cleanup_binary = dffml_feature_codesec.feature.operations:cleanup_binary.op',
        ],
        'dffml.operation.implementation': [
            'rpm_url_to_rpmfile = dffml_feature_codesec.feature.operations:RPMURLToRPMFile',
            'files_in_rpm = dffml_feature_codesec.feature.operations:files_in_rpm.imp',
            'binary_file = dffml_feature_codesec.feature.operations:binary_file.imp',
            'pwn_checksec = dffml_feature_codesec.feature.operations:pwn_checksec.imp',
            'cleanup_rpm = dffml_feature_codesec.feature.operations:cleanup_rpm.imp',
            'cleanup_binary = dffml_feature_codesec.feature.operations:cleanup_binary.imp',
        ],
    },
)
