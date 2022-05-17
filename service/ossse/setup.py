import ast
from io import open

from setuptools import find_packages, setup

with open('ossse/version.py', 'r') as f:
    for line in f:
        if line.startswith('VERSION'):
            version = ast.literal_eval(line.strip().split('=')[-1].strip())
            break

with open('README.rst', 'r', encoding='utf-8') as f:
    readme = f.read()

with open('requirements.txt', 'r', encoding='utf-8') as f:
    INSTALL_REQUIRES = [line for line in f]

setup(
    name='ossse',
    version=version,
    description='Open Source Software Data Collection',
    long_description=readme,
    author='John Andersen',
    author_email='johnandersenpdx@gmail.com',
    url='https://github.com/intel/dffml',
    license='',

    keywords=[
        '',
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],

    install_requires=INSTALL_REQUIRES,
    tests_require=[],

    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'ossse = ossse.cli:OSSSECLI.main',
        ],
    },
)
