Operations
==========

Operations Implementations are subclasses of
:class:`dffml.df.base.OperationImplementation`, they are functions or classes
which could do anything, make HTTP requests, do inference, etc.

They don't necessarily have to be written in Python. Although DFFML isn't quite
to the point where it can use operations written in other languages yet, it's on
the roadmap.

dffml
-----

.. code-block:: console

    pip install dffml


associate
~~~~~~~~~

*Official*

No description

**Stage: output**



**Inputs**

- spec: associate_spec(type: List[str])

**Outputs**

- output: associate_output(type: Dict[str, Any])

dffml.dataflow.run
~~~~~~~~~~~~~~~~~~

*Official*

No description

**Stage: processing**



**Inputs**

- inputs: flow_inputs(type: Dict[str,Any])

**Outputs**

- results: flow_results(type: Dict[str,Any])

**Args**

- dataflow: DataFlow

dffml.mapping.create
~~~~~~~~~~~~~~~~~~~~

*Official*

No description

**Stage: processing**



**Inputs**

- key: key(type: str)
- value: value(type: generic)

**Outputs**

- mapping: mapping(type: map)

dffml.mapping.extract
~~~~~~~~~~~~~~~~~~~~~

*Official*

No description

**Stage: processing**



**Inputs**

- mapping: mapping(type: map)
- traverse: mapping_traverse(type: List[str])

**Outputs**

- value: value(type: generic)

dffml.model.predict
~~~~~~~~~~~~~~~~~~~

*Official*

No description

**Stage: processing**



**Inputs**

- features: record_features(type: Dict[str, Any])

**Outputs**

- prediction: model_predictions(type: Dict[str, Any])

**Args**

- model: Entrypoint

get_single
~~~~~~~~~~

*Official*

No description

**Stage: output**



**Inputs**

- spec: get_single_spec(type: array)

**Outputs**

- output: get_single_output(type: map)

group_by
~~~~~~~~

*Official*

No description

**Stage: output**



**Inputs**

- spec: group_by_spec(type: Dict[str, Any])

**Outputs**

- output: group_by_output(type: Dict[str, List[Any]])

dffml_feature_git
-----------------

.. code-block:: console

    pip install dffml-feature-git


check_if_valid_git_repository_URL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Official*

No description

**Stage: processing**



**Inputs**

- URL: URL(type: string)

**Outputs**

- valid: valid_git_repository_URL(type: boolean)

cleanup_git_repo
~~~~~~~~~~~~~~~~

*Official*

No description

**Stage: cleanup**



**Inputs**

- repo: git_repository(type: Dict[str, str])

  - URL: str
  - directory: str

clone_git_repo
~~~~~~~~~~~~~~

*Official*

No description

**Stage: processing**



**Inputs**

- URL: URL(type: string)

**Outputs**

- repo: git_repository(type: Dict[str, str])

  - URL: str
  - directory: str

**Conditions**

- valid_git_repository_URL: boolean

count_authors
~~~~~~~~~~~~~

*Official*

No description

**Stage: processing**



**Inputs**

- author_lines: author_line_count(type: Dict[str, int])

**Outputs**

- authors: author_count(type: int)

git_commits
~~~~~~~~~~~

*Official*

No description

**Stage: processing**



**Inputs**

- repo: git_repository(type: Dict[str, str])

  - URL: str
  - directory: str
- branch: git_branch(type: str)
- start_end: date_pair(type: List[date])

**Outputs**

- commits: commit_count(type: int)

git_repo_author_lines_for_dates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Official*

No description

**Stage: processing**



**Inputs**

- repo: git_repository(type: Dict[str, str])

  - URL: str
  - directory: str
- branch: git_branch(type: str)
- start_end: date_pair(type: List[date])

**Outputs**

- author_lines: author_line_count(type: Dict[str, int])

git_repo_checkout
~~~~~~~~~~~~~~~~~

*Official*

No description

**Stage: processing**



**Inputs**

- repo: git_repository(type: Dict[str, str])

  - URL: str
  - directory: str
- commit: git_commit(type: string)

**Outputs**

- repo: git_repository_checked_out(type: Dict[str, str])

  - URL: str
  - directory: str
  - commit: str

git_repo_commit_from_date
~~~~~~~~~~~~~~~~~~~~~~~~~

*Official*

No description

**Stage: processing**



**Inputs**

- repo: git_repository(type: Dict[str, str])

  - URL: str
  - directory: str
- branch: git_branch(type: str)
- date: date(type: string)

**Outputs**

- commit: git_commit(type: string)

git_repo_default_branch
~~~~~~~~~~~~~~~~~~~~~~~

*Official*

No description

**Stage: processing**



**Inputs**

- repo: git_repository(type: Dict[str, str])

  - URL: str
  - directory: str

**Outputs**

- branch: git_branch(type: str)

**Conditions**

- no_git_branch_given: boolean

git_repo_release
~~~~~~~~~~~~~~~~

*Official*

Was there a release within this date range

**Stage: processing**



**Inputs**

- repo: git_repository(type: Dict[str, str])

  - URL: str
  - directory: str
- branch: git_branch(type: str)
- start_end: date_pair(type: List[date])

**Outputs**

- present: release_within_period(type: bool)

lines_of_code_by_language
~~~~~~~~~~~~~~~~~~~~~~~~~

*Official*

This operation relys on ``tokei``. Here's how to install version 10.1.1,
check it's releases page to make sure you're installing the latest version.

On Linux

.. code-block:: console

    $ curl -sSL 'https://github.com/XAMPPRocky/tokei/releases/download/v10.1.1/tokei-v10.1.1-x86_64-apple-darwin.tar.gz' \
      | tar -xvz && \
      echo '22699e16e71f07ff805805d26ee86ecb9b1052d7879350f7eb9ed87beb0e6b84fbb512963d01b75cec8e80532e4ea29a tokei' | sha384sum -c - && \
      sudo mv tokei /usr/local/bin/

On OSX

.. code-block:: console

    $ curl -sSL 'https://github.com/XAMPPRocky/tokei/releases/download/v10.1.1/tokei-v10.1.1-x86_64-apple-darwin.tar.gz' \
      | tar -xvz && \
      echo '8c8a1d8d8dd4d8bef93dabf5d2f6e27023777f8553393e269765d7ece85e68837cba4374a2615d83f071dfae22ba40e2 tokei' | sha384sum -c - && \
      sudo mv tokei /usr/local/bin/

**Stage: processing**



**Inputs**

- repo: git_repository_checked_out(type: Dict[str, str])

  - URL: str
  - directory: str
  - commit: str

**Outputs**

- lines_by_language: lines_by_language_count(type: Dict[str, Dict[str, int]])

lines_of_code_to_comments
~~~~~~~~~~~~~~~~~~~~~~~~~

*Official*

No description

**Stage: processing**



**Inputs**

- langs: lines_by_language_count(type: Dict[str, Dict[str, int]])

**Outputs**

- code_to_comment_ratio: language_to_comment_ratio(type: int)

quarters_back_to_date
~~~~~~~~~~~~~~~~~~~~~

*Official*

No description

**Stage: processing**



**Inputs**

- date: quarter_start_date(type: int)
- number: quarter(type: int)

**Outputs**

- date: date(type: string)
- start_end: date_pair(type: List[date])

work
~~~~

*Official*

No description

**Stage: processing**



**Inputs**

- author_lines: author_line_count(type: Dict[str, int])

**Outputs**

- work: work_spread(type: int)

dffml_feature_auth
------------------

.. code-block:: console

    pip install dffml-feature-auth


scrypt
~~~~~~

*Official*

No description

**Stage: processing**



**Inputs**

- password: UnhashedPassword(type: string)

**Outputs**

- password: ScryptPassword(type: string)