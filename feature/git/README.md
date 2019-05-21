# DFFML Features For Git Version Control

Git features scrape data from Git repositories.

## Demo

![Demo](https://github.com/intel/dffml/raw/master/docs/images/commits_demo.gif)

## Usage

Scrape lines of comments to lines of code ratio, diversity of authorship, number
of commits, number of authors, and frequency of release data for a given Git
repo.

```console
export OPIMPS="group_by quarters_back_to_date check_if_valid_git_repository_URL clone_git_repo git_repo_default_branch git_repo_checkout git_repo_commit_from_date git_repo_author_lines_for_dates work git_repo_release lines_of_code_by_language lines_of_code_to_comments git_commits count_authors cleanup_git_repo"
dffml operations repo \
  -log debug \
  -keys https://github.com/intel/dffml \
  -repo-def URL \
  -remap \
    group_by.cloc=cloc \
    group_by.release=release \
    group_by.work=work \
    group_by.commits=commits \
    group_by.authors=authors \
    group_by.relase=release \
  -dff-memory-operation-network-ops $OPIMPS \
  -dff-memory-opimp-network-opimps $OPIMPS \
  -inputs \
    {0,1,2,3,4,5,6,7,8,9}=quarter \
    "'2019-03-29 13:24'=quarter_start_date" \
    True=no_git_branch_given \
  -output-specs '{
      "cloc": {
        "group": "quarter",
        "by": "language_to_comment_ratio",
        "fill": 0
      },
      "authors": {
        "group": "quarter",
        "by": "author_count",
        "fill": 0
      },
      "work": {
        "group": "quarter",
        "by": "work_spread",
        "fill": 0
      },
      "release": {
        "group": "quarter",
        "by": "release_within_period",
        "fill": False
      },
      "commits": {
        "group": "quarter",
        "by": "commit_count",
        "fill": 0
      }
    }=group_by_spec'
```

## TODO

- Transforms
  - Take data of one defintion and label it as another definition.
```json
{
  "defintions": {},
  "operations": {},
  "transforms": {
    "quarter_date_to_git_date": {
      "quarter_date": ["git_date"]
    },
    "thing_to_other_data_types": {
      "thing": ["first_data_type", "second_data_type"]
    },
  },
}
```

## License

DFFML DFFML Features For Git Version Control are distributed under the
[MIT License](LICENSE).
