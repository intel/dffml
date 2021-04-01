1. 2nd and 3rd party plugins
============================

Date: 2021-04-01

Status
------

Draft

Context
-------

DFFML currency has the main package and all plugins maintained within a single
repo. We always intended to support 3rd party plugins, meaning displaying them
on the main docs site as options for users. We are just now getting around to
it.

We decided that we will have the main package, 2nd party plugins, and 3rd party
plugins.

- The main package is ``dffml``.

- 2nd party plugins are plugins that are maintained by the core maintainers and
  who's repos reside in the ``dffml`` organization.

- 3rd party plugins are hosted in user or other org repos and core maintainers
  are not owners of those repos.

We need to take the plugins that are currency maintained within the main repo
and put them in their own repos. We need the docs site to reflect the working /
not-working status of plugins on tutorial pages. We need to have a set of
plugins that we don't release unless those all work together. This is because a
core part of our functionality is letting users swap out underlying libraries,
which they can't do if they can't be installed together.

What do we know
~~~~~~~~~~~~~~~

- Main package has no dependencies

- The plugins page lists all plugins that are in ``dffml/plugins.py``

- There are tutorials that are associated with specific plugins

  - If a plugin's latest release doesn't pass CI against DFFML's latest
    release, any tutorials should show that it's not working.

- A main point of DFFML is to have a set of ML libraries that work together in
  a single install environment so that a user can try multiple libraries and
  choose the best one.

  - This means we have to know which plugins can be installed together.

Decision
--------

- We want to do the compatibility matrix check in the main plugin and in each
  plugin.

  - This lets the main plugin know at time of docs build, what status is for
    each plugin.

  - This lets plugin authors know in PR CI, etc. if they are about to cause a
    compatibility issue.

- We need the ability to move things from level 1 to level 2 if we want to
  deicide that that it's not longer a showstopper for release.

- Working / not-working status of tutorials we want to show two things
  This only applies to support levels 2 and 3. Because support levels 0 and 1
  must always work for release.

  - Does this tutorial work when other packages are installed latest / master?

  - Does this tutorial does work against all dependent packages for latest /
    master?

    - Some plugins rely only on the main package

      - Main package never has any dependencies. So from a dependency checking
        perspective, there should never be any issue.

    - Some plugin rely on other plugins as well

      - Main package never has any dependencies. So from a dependency checking
        perspective, there should never be any issue.

- To know which plugins can be installed together

  - Which plugins failure to validate against master branch warrant blocking
    release

    - We need some sort of support level tracking.

    - Support level tracking means test against latest release and master
      branch.

    - Possible support levels

      - 0 main package

      - 1 2nd party required pass for release

      - 2 2nd party not required pass for release

        - Note on tutorials that involve level 2 plugins to say they aren't
          working at the moment

      - 3 3rd party not required pass for release

        - Note on tutorials that involve level 3 plugins to say they aren't
          working at the moment

Consequences
------------

- Based on support levels

  - The ``dffml/plugins.json`` should list the plugin, and it's support level

- Documentation related to specific plugins

  - Tutorials that pip install packages of support level 2 or 3 must have some
    element that the top of the page that can show the working / not-working
    status.

  - When tutorials are tested, they only install the set of plugins that they
    need. So a tutorial CI test will fail if those plugins do not work together.
    Therefore, we display the warning because we know the tutorial works. If
    there is a failure to install all support level 1 and 2 plugins together, we
    know that we should display the warning. The tutorial works, but we're not
    sure what other other plugins installed in a same environment might cause
    dependency conflicts.

- Matrix check, two perspectives (this translates into CI tests)

  - Main package

    - Support level 1

      - For master, does installing all the plugins from their master zip
        archive URL work when all given to ``pip install`` at the same time.

      - For latest release, does installing all the plugins by PyPi name work
        when all given to ``pip install`` at the same time.

      - "work" here meaning does pip raise any issues about conflicting
        dependency versions.

    - Support level 2

      - For master

          - Does installing all the plugins in support levels 1 and 2 work from
            their master zip archive URL work when all given to ``pip install``
            at the same time.

            - PASS: No warning on tutorials.

            - FAIL: Warning on tutorials, this may not work when other plugins
              are install. This tutorial should still work when no other plugins
              are installed.

      - For latest release, does installing all the plugins by PyPi name work
        when all given to ``pip install`` at the same time.

          - Does installing all the plugins in support levels 1 and 2 work from
            their PyPi name when all given to ``pip install`` at the same time.

            - PASS: No warning on tutorials.

            - FAIL: Warning on tutorials, this may not work when other plugins
              are install. This tutorial should still work when no other plugins
              are installed.

      - "work" here meaning does pip raise any issues about conflicting
        dependency versions.

        - If they don't. Do we care about finding more info about which one's
          are braking it. No, we do not care, because figuring out matrix is
          exponential.

    - Support level 3

      - Always have a warning on tutorials, this may not work when other plugins
        are installed, because this a tutorial based on a third party plugin.
        This tutorial should still work when no other plugins are installed.
        In the event that it doesn't please report issues to third party here:
        <Link to third party project URL for plugin>

  - Plugin package

    - Support level 1

      - Fail CI if install of support level 1 plugins fails.

    - Support level 2

      - Fail CI if install of support level 1 plugins fails.

      - If there is some way to warn via CI. Then warn if install of support
        level 1 and 2 plugins fails.

    - Support level 3

      - Fail CI if install of support level 1 plugins fails.

      - If there is some way to warn via CI. Then warn if install of support
        level 1 and 2 plugins fails.
