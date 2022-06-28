CONTRIBUTING
############

This document describes how to write Open Architecture overlays,
overlays for Alice.

Data Flow Programming
*********************

Data Flow programming focueses on data types and data transformations.
Data Orented Design is also helpful in understanding Data Flow programming,
altough a distinct concept itself.

- https://en.wikipedia.org/wiki/Dataflow_programming
- https://www.gamedeveloper.com/programming/tips-on-writing-code-for-data-oriented-design
- https://www.youtube.com/watch?v=aPh4Z3SioB8

Finding Data Types to Work With
*******************************

**TODO** Finish this section

.. code-block:: console

    $ dffml service list entrypoints dffml.overlays`

Writing an Overlay
******************

Overlays can be as simple as functions. Or they

References for writing operations. Including examples with networking:

- https://intel.github.io/dffml/alice/examples/shouldi.html

.. code-block:: python

    import json
    import 
    
    from alice.overlays.git import AliceGitRepo

    from typing import NewType

    MyConfig = NewType("MyConfig", object)
    MyConfigUnvalidated = NewType("MyConfigUnvalidated", object)
    MyConfigProjectName = NewType("MyConfigProjectName", str)

    def read_my_config_if_exists(
        repo: AliceGitRepo,
    ) -> MyConfig:
        path = patlib.Path(repo.directory, ".my_config.json")
        return json.loads(path.read_text())

    def validate_my_config(
        config: MyConfigUnvalidated,
    ) -> MyConfig:
        # TODO(security) json schema valiation of myconfig (or
        # make done automatically by operation manifest schema
        # validation on InputNetwork)
        return config

    def my_config_project_name(
        config: MyConfig,
    ) -> MyConfigProjectName:
        return config["name"]

Registering an Overlay
**********************

**entry_points.txt**

.. code-block::

    [dffml.overlays]
    alice.please.contribute.read_my_config_if_exists = alice.overalys.my_new_overlay:read_my_config_if_exists
    alice.please.contribute.my_config_project_name = alice.overalys.my_new_overlay:my_config_project_name
    alice.please.contribute.validate_my_config = alice.overalys.my_new_overlay:validate_my_config

Debugging
*********

.. code-block:: console

    $ python -m pdb -m alice
