import dffml
from typing import NewType

from .todos import AlicePleaseLogTodosDataFlowRecommendedCommnuityStandardsGitHubIssues


CreatedIssuesURLs = NewType("CreatedIssuesURLs", dict)


@dffml.op(
    stage=dffml.Stage.OUTPUT,
)
def grab_created_urls(
    support: AlicePleaseLogTodosDataFlowRecommendedCommnuityStandardsGitHubIssues.SupportIssueURL,
    code_of_conduct: AlicePleaseLogTodosDataFlowRecommendedCommnuityStandardsGitHubIssues.CodeOfConductIssueURL,
    contributing: AlicePleaseLogTodosDataFlowRecommendedCommnuityStandardsGitHubIssues.ContributingIssueURL,
    security: AlicePleaseLogTodosDataFlowRecommendedCommnuityStandardsGitHubIssues.SecurityIssueURL,
    readme: AlicePleaseLogTodosDataFlowRecommendedCommnuityStandardsGitHubIssues.ReadmeIssueURL,
) -> CreatedIssuesURLs:
    return {
        "support": support,
        "code_of_conduct": code_of_conduct,
        "contributing": contributing,
        "security": security,
        "readme": readme,
    }
