# Upstream First Development in Federated Software Forges

> prompt(model:gpt-4o): Explain what upstream first is: Explain how federation of software forges (such as gitea and gitlab and github, similar to how threads and mastodon federate via activitypub) which form ad-hoc organizations in pursuit of shared strategic principles and plans can practice upstream first development using github pull request style workflow. Return your response as a markdown file which will be included in the documentation for the forgejo project. Please go into detail. https://chatgpt.com/share/bc6fc7c3-aa76-4518-9d41-0d5107b92f52

## Introduction

In a federated environment where various software forges like Gitea, GitLab, and GitHub interact similarly to social platforms like Threads and Mastodon via ActivityPub, the practice of "upstream first" development can be efficiently managed. This document outlines how these federated forges can form ad-hoc organizations to pursue shared strategic principles and plans while adhering to the upstream first development model using a GitHub pull request style workflow.

## Key Concepts

### Federation of Software Forges
Federation allows independent software forges to communicate and collaborate seamlessly. Each forge retains its autonomy while contributing to a larger ecosystem. This is similar to how social networks federate, enabling users from different platforms to interact. Federation in the context of software development means:
- **Interoperability**: Different forges can work together, sharing code and issues.
- **Decentralization**: Each forge operates independently but can contribute to and pull from a common pool of projects.
- **Collaboration**: Developers from different forges can collaborate on the same project as if they were using the same platform.

### Upstream First Development
This development practice involves contributing changes, enhancements, or bug fixes to the original project (upstream) before integrating them into downstream projects or forks. It promotes:
- **Shared Improvement**: Enhancements benefit all users of the upstream project.
- **Simplified Maintenance**: Reduces the need for maintaining separate patches.
- **Better Collaboration**: Encourages cooperation between developers.
- **Avoiding Divergence**: Keeps downstream projects aligned with upstream changes.

## Workflow for Upstream First Development

### 1. Identify and Plan the Change

#### Shared Strategic Principles and Plans
Federated forges often form ad-hoc organizations to pursue common goals. These organizations should identify strategic principles and plans guiding their development efforts. These principles might include:
- **Open Collaboration**: Encouraging contributions from any developer in the federation.
- **Transparency**: Keeping development discussions and decisions open and accessible.
- **Quality and Security**: Ensuring that all contributions meet high standards for quality and security.

#### Issue Tracking
Use a federated issue tracking system to identify and discuss the change needed. Each forge can contribute to the discussion regardless of where the issue was originally reported. This can be managed through:
- **Federated Issue Boards**: A shared space where issues from all participating forges are tracked and prioritized.
- **Discussion Threads**: Forums or discussion threads where developers can propose solutions and collaborate on ideas.

### 2. Develop the Change

#### Local Development
Developers work on their local forks or branches of the project. Ensure the changes align with the upstream project's guidelines and standards. Best practices include:
- **Consistent Coding Standards**: Adhering to the coding guidelines of the upstream project.
- **Unit Tests**: Writing tests to ensure the change works as intended.
- **Documentation**: Updating documentation to reflect the changes.

#### Collaborative Effort
Utilize federation capabilities to collaborate with developers across different forges. Tools like federated code review and discussion can be beneficial here. Techniques include:
- **Pair Programming**: Working together with developers from different forges.
- **Federated Code Reviews**: Using tools that allow for code reviews across different forges.

### 3. Submit a Pull Request (PR)

#### Upstream Repository
Once the change is ready, submit a pull request to the upstream repository. This is done in the forge where the original project is hosted. Key steps include:
- **Fork and Branch**: Fork the upstream repository and create a branch for your changes.
- **Commit Changes**: Ensure each commit is clear and concise.
- **Open PR**: Open a pull request with a detailed description of the changes.

#### Federated PRs
Federated forges should support cross-forge pull requests, allowing a pull request from a repository on one forge to be reviewed and merged into a repository on another forge. This involves:
- **Federated Pull Request Tools**: Tools that allow PRs to be initiated from any forge and integrated with the upstream project.
- **ActivityPub Integration**: Using protocols like ActivityPub to manage communication between forges.

### 4. Review and Collaborate

#### Code Review
Engage in a thorough code review process. Federated forges can allow reviewers from different platforms to comment and approve changes. Best practices include:
- **Multiple Reviewers**: Ensure the PR is reviewed by multiple developers.
- **Automated Testing**: Use CI/CD to run automated tests on the PR.
- **Feedback Loop**: Address feedback promptly and update the PR as necessary.

#### Continuous Integration
Utilize CI/CD pipelines that work across federated environments to ensure changes meet quality standards. This involves:
- **Federated CI/CD Tools**: CI/CD tools that can pull code from different forges and run tests.
- **Integration Tests**: Running comprehensive integration tests to ensure the change works across all environments.

### 5. Merge and Integrate

#### Upstream Merge
Once the pull request is approved, it is merged into the upstream project. This ensures the change benefits the entire community. Steps include:
- **Final Review**: A final review by the maintainers.
- **Merge**: Using a merge strategy that maintains a clean commit history.

#### Downstream Synchronization
Downstream projects can then pull the latest changes from the upstream project. This keeps all forks and derivatives up-to-date with the latest improvements. This involves:
- **Regular Updates**: Downstream projects should regularly pull changes from upstream.
- **Conflict Resolution**: Address any conflicts that arise during the merge.

### 6. Communication and Documentation

#### Federated Communication
Use federated communication tools to keep all stakeholders informed about the progress and integration of changes. This includes:
- **Announcements**: Announcing major changes and updates across all forges.
- **Discussion Forums**: Maintaining forums or chat channels for ongoing communication.

#### Documentation Updates
Ensure that any changes are well-documented. Documentation should be accessible across all federated forges. This involves:
- **Documentation PRs**: Submitting PRs to update documentation alongside code changes.
- **Shared Documentation Repositories**: Repositories that aggregate documentation from different forges.

## Benefits of This Workflow

- **Shared Improvements**: Contributions benefit the entire ecosystem, not just individual forges.
- **Reduced Maintenance Burden**: By integrating changes upstream first, the need for maintaining separate patches and re-integration efforts is minimized.
- **Enhanced Collaboration**: Federated tools and workflows foster better collaboration across different platforms.
- **Consistency**: Ensures all projects derived from the upstream source remain consistent and compatible.

## Conclusion

By adopting an upstream first development practice in a federated environment, software forges can collaborate more effectively and ensure that improvements benefit the broader community. This workflow, modeled on the GitHub pull request style, leverages the strengths of federation to create a more cohesive and high-quality software development ecosystem.

For more details on federation and how to get involved, visit the [Forgejo Project](https://forgejo.org).