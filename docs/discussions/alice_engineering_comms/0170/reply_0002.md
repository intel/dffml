## 2023-02-06 Exporting Groovy Functions

- 1:1 Pankaj/John

```console
$ git remote -v
origin https://github.com/owner/repository
$ git status
origin    https://github.com/owner/repository
```

- `origin/branch_name` -> https://github.com/owner/repository/blob/branch_name
- https://github.com/intel/dffml/issues/1433


```mermaid
graph LR

  subgraph AliceShouldIContribute
    repo_directory
    subgraph examples_operations[dffml.git examples.operations]
      repo_directory --> python_parse_ast
    end
    python_parse_ast --> python_ast_module_scope_exported
    python_ast_module_scope_exported --> python_functions
  end

  subgraph KnowledgeGraph[Rapunzel/ActivityPubSecurityTxt]
    record[Repo]
    subgraph features
      python_functions -->|list of all outputs from all executions populates| PythonFunctions
    end

    record --> PythonFunctions
  end

  subgraph ContextRender
    versioned_learning -->|List of granular items within record, docs| granular_inventory_items

    granular_inventory_items -->|itertools.contact list of items for discovered within each item, seconds within docs, features.python_ast_exports_analogus_to_dffml_init| record
  end
```

- TODO
  - [x] Pull request DFFML
    - https://github.com/intel/dffml/pull/1432
  - [x] Merge PR
  - [x] Rebuild container
    - https://github.com/intel/dffml/blob/main/.github/workflows/dffml_build_images_containers.yml
  - [x] Kick off run single
    - `alice shouldi contribute -keys https://github.com/jenkinsci/kubernetes-plugin`