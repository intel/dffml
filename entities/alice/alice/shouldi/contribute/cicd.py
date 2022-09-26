from typing import NewType

import dffml
import dffml_operations_innersource.operations


IsCICDJenkinsLibrary = NewType("IsCICDJenkinsLibrary", bool)
IsCICDGitHubActionsLibrary = NewType("IsCICDGitHubActionsLibrary", bool)
CICDLibrary = NewType("CICDLibrary", dict)


@dffml.op(
    stage=dffml.Stage.OUTPUT,
)
def cicd_library(
    self,
    cicd_jenkins_library: IsCICDJenkinsLibrary,
    cicd_action_library: IsCICDGitHubActionsLibrary,
) -> CICDLibrary:
    return {
        "cicd-jenkins-library": cicd_jenkins_library,
        "cicd-action-library": cicd_action_library,
    }


@dffml.op(
    stage=dffml.Stage.OUTPUT,
)
def cicd_jenkins_library(
    self,
    groovy_file_paths: dffml_operations_innersource.operations.GroovyFileWorkflowUnixStylePath,
) -> IsCICDJenkinsLibrary:
    return bool(groovy_file_paths)


@dffml.op(
    stage=dffml.Stage.OUTPUT,
)
def cicd_action_library(
    self,
    action_file_paths: dffml_operations_innersource.operations.ActionYAMLFileWorkflowUnixStylePath,
) -> IsCICDGitHubActionsLibrary:
    return bool(action_file_paths)
