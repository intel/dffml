from typing import NewType

import dffml
import dffml_operations_innersource.operations
import pathlib


IsCICDJenkinsLibrary = NewType("IsCICDJenkinsLibrary", bool)
IsCICDGitHubActionsLibrary = NewType("IsCICDGitHubActionsLibrary", bool)
CICDLibrary = NewType("CICDLibrary", dict)
GroovyFunctions = NewType("GroovyFunctions",list[str])


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

@dffml.op
def groovy_functions(
    repo_directory: dffml_operations_innersource.operations.RepoDirectory,
    groovy_file_path: dffml_operations_innersource.operations.GroovyFileWorkflowUnixStylePath,
) -> GroovyFunctions:
    from pathlib import Path
    txt = Path(repo_directory,groovy_file_path).read_text().splitlines()
    new_list = []
    idx = 0
    text = "void"
    for line in txt:

            # if line have the input string, get the index
            # of that line and put the
            # line into newly created list
            if line.lstrip()[:4] == "void":
                line = line.split('(',1)[0]
                line = line.split('void',1)[1].strip()
                new_list.insert(idx, line)
                idx += 1

        # closing file after reading
        #file_read.close()

        # if length of new list is 0 that means
        # the input string doesn't
        # found in the text file
    if len(new_list)==0:
        print("\n\"" +text+ "\" is not found in file\"" "\"!")
    else:

        # displaying the lines
        # containing given string
        lineLen = len(new_list)

        print("\n**** Lines containing \"" +text+ "\" ****\n")
        for i in range(lineLen):
            print(end=new_list[i])
            print("\n")
        return new_list
