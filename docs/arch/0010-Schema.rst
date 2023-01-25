10. Schema
==========

Date: 2023-01-25

Status
------

Accepted

Context
-------

We have accepted the `Manifest ADR <https://github.com/intel/dffml/blob/alice/docs/arch/0008-Manifest.md>`_.

This document describes how we will implement versioned learning for
continuous improvement.

- References

  - ``Rolling Alice: Coach Alice: Versioning Learning``
  - https://mastodon.social/@kidehen/109661888985882857

    - Data with schema generation using "AI" extraction
    - "Another GPT-Chat structured data generation exercise that pleasantly surprised me by the outcome. Prompt comprising Markmap variant of #Markdown for entity relationship graph visualization" [Kingsley Uyi Idehen - @kidehen@mastodon.soc]
    - We are going to end up with a knowledge graph and work to understand the differences in the data via schema and data analysis.

  - https://github.com/lysander07/Presentations/raw/main/EGC2023_Symbolic%20and%20Subsymbolic%20AI%20%20-%20an%20Epic%20Dilemma.pdf

Decision
--------

We document data model information via a hybrid of intent via a ``README.md`` or
``README.rst``.

Consequences
------------

When documenting data models, they are completely documented when they have
the following:

- At least one versionned schema file within the schema directory.

  - ``0.0.1.schema.json``

- A manifest ADR style description of the data model and the intent of usage.

  - ``README.md``

- At least one example which validates against the latest schema.

  - ``example-pass.json``

At a high level the process is

- Target data model is generated from manifest schema

- Given an `OperationImplementation` output of target manifest data model type

  - On dataflow operation input dependency tree changes (before: Down the Dependency Rabbit Hole Again, before: Cartographer Extraordinaire) update `/schema/*` via `datamodel-code-gen.py`

    - If code or tree changes, bump minor

      - Can always manually rename and commit file to dot

    - If input tree changes, bump major

    - Pre-commit hooks and CI to validate
