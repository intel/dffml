import os
import ast
from io import open

from setuptools import find_packages, setup

self_path = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(self_path, 'dffml_feature_git', 'version.py'),
          'r') as f:
    for line in f:
        if line.startswith('VERSION'):
            version = ast.literal_eval(line.strip().split('=')[-1].strip())
            break

with open(os.path.join(self_path, 'README.md'), 'r', encoding='utf-8') as f:
    readme = f.read()

INSTALL_REQUIRES = [
    "python-dateutil>=2.7.3"
    ]

setup(
    name='dffml_feature_git',
    version=version,
    description='',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='John Andersen',
    author_email='john.s.andersen@intel.com',
    url='https://github.com/intel/dffml/blob/master/feature/git/README.md',
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
            'quarters_back_to_date = dffml_feature_git.feature.operations:quarters_back_to_date.op',
            'check_if_valid_git_repository_URL = dffml_feature_git.feature.operations:check_if_valid_git_repository_URL.op',
            'clone_git_repo = dffml_feature_git.feature.operations:clone_git_repo.op',
            'git_repo_default_branch = dffml_feature_git.feature.operations:git_repo_default_branch.op',
            'git_repo_checkout = dffml_feature_git.feature.operations:git_repo_checkout.op',
            'git_repo_commit_from_date = dffml_feature_git.feature.operations:git_repo_commit_from_date.op',
            'git_repo_author_lines_for_dates = dffml_feature_git.feature.operations:git_repo_author_lines_for_dates.op',
            'work = dffml_feature_git.feature.operations:work.op',
            'git_repo_release = dffml_feature_git.feature.operations:git_repo_release.op',
            'lines_of_code_by_language = dffml_feature_git.feature.operations:lines_of_code_by_language.op',
            'lines_of_code_to_comments = dffml_feature_git.feature.operations:lines_of_code_to_comments.op',
            'git_commits = dffml_feature_git.feature.operations:git_commits.op',
            'count_authors = dffml_feature_git.feature.operations:count_authors.op',
            'cleanup_git_repo = dffml_feature_git.feature.operations:cleanup_git_repo.op',
        ],
        'dffml.operation.implementation': [
            'quarters_back_to_date = dffml_feature_git.feature.operations:quarters_back_to_date.imp',
            'check_if_valid_git_repository_URL = dffml_feature_git.feature.operations:check_if_valid_git_repository_URL.imp',
            'clone_git_repo = dffml_feature_git.feature.operations:clone_git_repo.imp',
            'git_repo_default_branch = dffml_feature_git.feature.operations:git_repo_default_branch.imp',
            'git_repo_checkout = dffml_feature_git.feature.operations:git_repo_checkout.imp',
            'git_repo_commit_from_date = dffml_feature_git.feature.operations:git_repo_commit_from_date.imp',
            'git_repo_author_lines_for_dates = dffml_feature_git.feature.operations:git_repo_author_lines_for_dates.imp',
            'work = dffml_feature_git.feature.operations:work.imp',
            'git_repo_release = dffml_feature_git.feature.operations:git_repo_release.imp',
            'lines_of_code_by_language = dffml_feature_git.feature.operations:lines_of_code_by_language.imp',
            'lines_of_code_to_comments = dffml_feature_git.feature.operations:lines_of_code_to_comments.imp',
            'git_commits = dffml_feature_git.feature.operations:git_commits.imp',
            'count_authors = dffml_feature_git.feature.operations:count_authors.imp',
            'cleanup_git_repo = dffml_feature_git.feature.operations:cleanup_git_repo.imp',
        ],
    },
)
