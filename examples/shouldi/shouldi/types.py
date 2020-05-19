from dffml import Definition

from typing import NamedTuple


class SAResultsSpec(NamedTuple):
    """
    Static analysis results for a language
    """

    critical: int
    high: int
    medium: int
    low: int
    report: dict


SA_RESULTS = Definition(
    name="static_analysis", primitive="string", spec=SAResultsSpec,
)
