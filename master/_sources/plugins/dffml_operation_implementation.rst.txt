Operation Implementations
=========================

Operations Implementations are subclasses of
:class:`dffml.df.base.OperationImplementation`, they are functions or classes
which could do anything, make HTTP requests, do inference, etc.

dffml
-----

.. code-block:: console

    pip install dffml


associate
~~~~~~~~~

*Core*

No description

**Stage: output**



**Inputs**

- spec: associate_spec(type: List[str])

**Outputs**

- output: associate_output(type: Dict[str, Any])

get_single
~~~~~~~~~~

*Core*

No description

**Stage: output**



**Inputs**

- spec: get_single_spec(type: List[str])

**Outputs**

- output: get_single_output(type: Dict[str, Any])

group_by
~~~~~~~~

*Core*

No description

**Stage: output**



**Inputs**

- spec: group_by_spec(type: Dict[str, Any])

  - group: Definition
  - by: Definition
  - fill: typing.Any

**Outputs**

- output: group_by_output(type: Dict[str, List[Any]])

dffml_feature_git
-----------------

.. code-block:: console

    pip install dffml-feature-git


check_if_valid_git_repository_URL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Core*

No description

**Stage: processing**



**Inputs**

- URL: URL(type: string)

**Outputs**

- valid: valid_git_repository_URL(type: boolean)

cleanup_git_repo
~~~~~~~~~~~~~~~~

*Core*

No description

**Stage: cleanup**



**Inputs**

- repo: git_repository(type: Dict[str, str])

clone_git_repo
~~~~~~~~~~~~~~

*Core*

No description

**Stage: processing**



**Inputs**

- URL: URL(type: string)

**Outputs**

- repo: git_repository(type: Dict[str, str])

**Conditions**

- valid_git_repository_URL: boolean

count_authors
~~~~~~~~~~~~~

*Core*

No description

**Stage: processing**



**Inputs**

- author_lines: author_line_count(type: Dict[str, int])

**Outputs**

- authors: author_count(type: int)

git_commits
~~~~~~~~~~~

*Core*

No description

**Stage: processing**



**Inputs**

- repo: git_repository(type: Dict[str, str])
- branch: git_branch(type: str)
- start_end: date_pair(type: List[date])

**Outputs**

- commits: commit_count(type: int)

git_repo_author_lines_for_dates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Core*

No description

**Stage: processing**



**Inputs**

- repo: git_repository(type: Dict[str, str])
- branch: git_branch(type: str)
- start_end: date_pair(type: List[date])

**Outputs**

- author_lines: author_line_count(type: Dict[str, int])

git_repo_checkout
~~~~~~~~~~~~~~~~~

*Core*

No description

**Stage: processing**



**Inputs**

- repo: git_repository(type: Dict[str, str])
- commit: git_commit(type: string)

**Outputs**

- repo: git_repository_checked_out(type: Dict[str, str])

git_repo_commit_from_date
~~~~~~~~~~~~~~~~~~~~~~~~~

*Core*

No description

**Stage: processing**



**Inputs**

- repo: git_repository(type: Dict[str, str])
- branch: git_branch(type: str)
- date: date(type: string)

**Outputs**

- commit: git_commit(type: string)

git_repo_default_branch
~~~~~~~~~~~~~~~~~~~~~~~

*Core*

No description

**Stage: processing**



**Inputs**

- repo: git_repository(type: Dict[str, str])

**Outputs**

- branch: git_branch(type: str)

**Conditions**

- no_git_branch_given: boolean

git_repo_release
~~~~~~~~~~~~~~~~

*Core*

No description

**Stage: processing**



**Inputs**

- repo: git_repository(type: Dict[str, str])
- branch: git_branch(type: str)
- start_end: date_pair(type: List[date])

**Outputs**

- present: release_within_period(type: bool)

lines_of_code_by_language
~~~~~~~~~~~~~~~~~~~~~~~~~

*Core*

No description

**Stage: processing**



**Inputs**

- repo: git_repository_checked_out(type: Dict[str, str])

**Outputs**

- lines_by_language: lines_by_language_count(type: Dict[str, Dict[str, int]])

lines_of_code_to_comments
~~~~~~~~~~~~~~~~~~~~~~~~~

*Core*

No description

**Stage: processing**



**Inputs**

- langs: lines_by_language_count(type: Dict[str, Dict[str, int]])

**Outputs**

- code_to_comment_ratio: language_to_comment_ratio(type: int)

quarters_back_to_date
~~~~~~~~~~~~~~~~~~~~~

*Core*

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

*Core*

No description

**Stage: processing**



**Inputs**

- author_lines: author_line_count(type: Dict[str, int])

**Outputs**

- work: work_spread(type: int)

dffml_operations_binsec
-----------------------

.. code-block:: console

    pip install dffml-operations-binsec


cleanup_rpm
~~~~~~~~~~~

*Core*

No description

**Stage: cleanup**



**Inputs**

- rpm: RPMObject(type: python_obj)

files_in_rpm
~~~~~~~~~~~~

*Core*

No description

**Stage: processing**



**Inputs**

- rpm: RPMObject(type: python_obj)

**Outputs**

- files: rpm_filename(type: str)

is_binary_pie
~~~~~~~~~~~~~

*Core*

No description

**Stage: processing**



**Inputs**

- rpm: RPMObject(type: python_obj)
- filename: rpm_filename(type: str)

**Outputs**

- is_pie: binary_is_PIE(type: bool)

url_to_urlbytes
~~~~~~~~~~~~~~~

*Core*

No description

**Stage: processing**



**Inputs**

- URL: URL(type: string)

**Outputs**

- download: URLBytes(type: python_obj)

urlbytes_to_rpmfile
~~~~~~~~~~~~~~~~~~~

*Core*

No description

**Stage: processing**



**Inputs**

- download: URLBytes(type: python_obj)

**Outputs**

- rpm: RPMObject(type: python_obj)

urlbytes_to_tarfile
~~~~~~~~~~~~~~~~~~~

*Core*

No description

**Stage: processing**



**Inputs**

- download: URLBytes(type: python_obj)

**Outputs**

- rpm: RPMObject(type: python_obj)

dffml_feature_auth
------------------

.. code-block:: console

    pip install dffml-feature-auth


scrypt
~~~~~~

*Core*

No description

**Stage: processing**



**Inputs**

- password: UnhashedPassword(type: string)

**Outputs**

- password: ScryptPassword(type: string)