import os
import sys
import ast
import subprocess
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

git_rpmfile = 'git+https://github.com/pdxjohnny/rpmfile@subfile_close'

try:
    import rpmfile
except (ModuleNotFoundError, ImportError):
    if '--user' in sys.argv:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade',
            '--user', git_rpmfile], check=False)
    else:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade',
            git_rpmfile], check=False)

setup(
    name='dffml_feature_codesec',
    version=version,
    description='',
    long_description=readme,
    long_description_content_type='text/markdown',
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
            'url_to_urlbytes = dffml_feature_codesec.feature.operations:url_to_urlbytes',
            'urlbytes_to_tarfile = dffml_feature_codesec.feature.operations:urlbytes_to_tarfile.op',
            'urlbytes_to_rpmfile = dffml_feature_codesec.feature.operations:urlbytes_to_rpmfile.op',
            'files_in_rpm = dffml_feature_codesec.feature.operations:files_in_rpm.op',
            'is_binary_pie = dffml_feature_codesec.feature.operations:is_binary_pie',
            'cleanup_rpm = dffml_feature_codesec.feature.operations:cleanup_rpm.op',
        ],
        'dffml.operation.implementation': [
            'url_to_urlbytes = dffml_feature_codesec.feature.operations:URLToURLBytes',
            'urlbytes_to_tarfile = dffml_feature_codesec.feature.operations:urlbytes_to_tarfile.imp',
            'urlbytes_to_rpmfile = dffml_feature_codesec.feature.operations:urlbytes_to_rpmfile.imp',
            'files_in_rpm = dffml_feature_codesec.feature.operations:files_in_rpm.imp',
            'is_binary_pie = dffml_feature_codesec.feature.operations:IsBinaryPIE',
            'cleanup_rpm = dffml_feature_codesec.feature.operations:cleanup_rpm.imp',
        ],
    },
)
