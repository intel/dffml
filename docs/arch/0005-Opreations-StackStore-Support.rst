5. Operations: StackStore Support
=================================

Date: 2021-07-19

Status
------

Draft

Context
-------

StackStore is a similar project to DFFML. They have concepts similar to
operations. They have a library of operations with their implement ions. We can
leverage their library by exposing their integrations pack actions as
operations.

Integration packs are usually installed via the StackStore CLI. They have
configurations which effect all actions within their pack.


Decision
--------

We can download actions by their git repo tags from GitHub. We can create python
packages of them and use pip to install locally.

We will parse the action YAML files and pack configs. Each action will become an
operation and we'll make configuration at the operation scope, rather than the
pack.

Consequences
------------
