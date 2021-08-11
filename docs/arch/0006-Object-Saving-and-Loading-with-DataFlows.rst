6. Object Saving and Loading with DataFlows
===========================================

Date: 2021-08-10

Status
------

Draft

Context
-------

This is a follow on to 0004-Model-Saving-and-Loading. This document outlines our
plan to implement a generic saving and load mechanism for all
:py:class:`BaseConfigurable <dffml.base.BaseConfigurable>` objects.
See the 2021-08-10 Weekly Sync Meeting recording for more details.

Decision
--------

save and load of any object

- save

  - Takes the object and (a dataflow or a location)

    - If a location is given we run the code to create a dataflow which saves to
      the given location

    - Pass as inputs to the dataflow

        - plugin type (model)

        - which plugin (scikitlr)

        - the config (pass through :py:func:`export <dffml.util.data.export>`
          first).

Consequences
------------

