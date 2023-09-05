# 2022-09-13 Engineering Logs

- GSoC 2022
  - https://summerofcode.withgoogle.com/organizations/python-software-foundation/projects/details/4tE547Oz
  - https://summerofcode.withgoogle.com/organizations/python-software-foundation/projects/details/gNdNxmFb
- OpenSSF
  - SBOM Everywhere
    - https://github.com/ossf/sbom-everywhere/issues/12
    - https://docs.google.com/document/d/1iCL7NOSxIc7YpVI2NRANIy46pM-02G_WlPexQqqb2R0/edit
      - > - Level 1: clients and SDKs — Operating system and build system-agnostic command line interpreters (CLIs) that can process source and build output artifacts / as well as process operating system and other dependencies. That output a compliant SBOM that includes the necessary data that addresses all use cases. These tools should be able to be run in a manual or automated (e.g., scripted) fashion as part of an end-to-end CI/CD workflow. These tools will include SDKs that developers can use to customize and extend any base tools, for instance to support additional package managers.
        > - Level 2: package manager plugins — a set of plugins or modules that work natively with the major package managers and repositories such as Maven, npm, and PyPI. These tools will typically require a single line configuration change added in order to run with each subsequent build and will output compliant SBOMs. This work will enhance the best existing open source plugins where they exist.
        > - Level 3: native package manager integration — by adding native SBOM generation functionality to major package managers, all developers and all build systems will automatically generate SBOMs by default as part of their normal workflow. SBOM generation will become as common and seamless as tooling creating log entries for software builds in a log file behind the scenes.
        > - Level 4: containerization integration — by adding native SBOM generation functionality to the containerization build process, the system will use SBOM content provided by included packages plus additional artifacts added during container build to output an SBOM that specifies all the components that make up a container.
        > - Level 5: application/solution integration/deployment — When deploying an application consisting of multiple disparate components (containers, machine images, event driven services) the coordination manager should aggregate the constituent SBOMS to reflect all artifacts that are deployed.