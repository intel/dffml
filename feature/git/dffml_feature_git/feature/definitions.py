import sys

from dffml.df.base import Definition

definitions = [
    Definition(
        name="quarter_start_date",
        primitive="int"
    ),
    Definition(
        name="quarter",
        primitive="int",
    ),
    Definition(
        name="URL",
        primitive="string",
    ),
    Definition(
        name="valid_git_repository_URL",
        primitive="boolean",
    ),
    Definition(
        name="git_branch",
        primitive="str",
    ),
    Definition(
        name="git_repository",
        primitive="Dict[str, str]",
        lock=True
    ),
    Definition(
        name="git_repository_checked_out",
        primitive="Dict[str, str]",
        lock=True
    ),
    Definition(
        name="git_commit",
        primitive="string"
    ),
    Definition(
        name="date",
        primitive="string"
    ),
    Definition(
        name="no_git_branch_given",
        primitive="boolean"
    ),
    Definition(
        name="date_pair",
        primitive="List[date]"
    ),
    Definition(
        name="author_line_count",
        primitive="Dict[str, int]"
    ),
    Definition(
        name="work_spread",
        primitive="int"
    ),
    Definition(
        name="release_within_period",
        primitive="bool"
    ),
    Definition(
        name="lines_by_language_count",
        primitive="Dict[str, Dict[str, int]]"
    ),
    Definition(
        name="language_to_comment_ratio",
        primitive="int"
    ),
    Definition(
        name="commit_count",
        primitive="int"
    ),
    Definition(
        name="author_count",
        primitive="int"
    ),
    Definition(
        name="date_generator_spec",
        primitive="Dict[str, Any]"
    )
]

for definition in definitions:
    setattr(sys.modules[__name__], definition.name, definition)
