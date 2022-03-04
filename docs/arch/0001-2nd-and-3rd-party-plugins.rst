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

Notes
-----

tutorial check command 

this command will help us check if a tutorial by providing its URL is compatible with the locally installed version of the FML and all available plugins that are installed 

check if URL to tutorial  we could push a Jason file or some sort of metadata into the I built doc so that we can check maybe a unique ID and the unique ID then you know build some Jason files well what we do is we output UM you know probably some kind of structure within the document that lets us determine what the versions of the plugins that the document were looking at was tested against

dependency declaration

we need some sort of file maybe espam format which declares all of our dependencies we can then do a you know take this format converted into something that can be pip installed and then we do a PIP download in one of the stages of the CI job we upload the downloaded artifact into the next stage of the CI job and then we you know install it or yeah no we we oh we set that as the index basically so we take these downloaded files and pip only well we expose them on a local file server or something or or maybe you can use the file URL for the index uhm URL of pip in this way the test cases are only allowed to install things which have been declared in whatever you know dependency format for example espam ah so

PR validation

essentially trigger a domino effect where we analyze the requirements files of all of the plugins that are either first or second party possibly support third party later somehow uhm and we build a dependency tree to understand which packages or which plugins are dependent on the plug in which is being changed in the original pull request we run the validation for the original pull request and then we run validation against you we trigger all of the CI runs of all of the downstream projects with the PR applied to with the original PR applied at if any of the downstream repos have would need to be changed for their CI to pass we can create PR's against those repos in the original PR we can provide overrides for each dependency so that when we trigger the validation or not dependency but downstream package so that when we trigger the validation for each downstream package we can say use this PR so if you've made an API breaking change and you need to go through all of the downstream dependencies are and make changes and submit PR that would make it OK then you go and then you specify you know all of those PRs which will be used when running the CI of the downstream dependencies respectively

We should also make sure to support 3rd party plugin's abilities to revalidate against any of their dependencies, whenever one of their dependencies changes. Possibly some kind of service people can set as a webhook which is a sort of pubsub. The SCM sever such as GitHub publishes webhook events to the service (`dffml-service-sw-src-change-notify`). The service then relays to any listeners. Listeners are downstream projects. Downstream projects can register themselves with the listener to receive change events for any of their dependencies. Registration involves plugin based configurable callbacks.

Repo locks

for this what amounts to essentially a Poly repo structure to work we with the way that we're validating all of our poor requests against each other before merge we need to ensure that when the original PR is merged all the rest of the PR's associated with it that might you know fix API breaking changes in downstream dependent packages are also merged therefore we will need some sort of a system account or bot to which has which must approve every pull request and that bot we can make the logic so that if there is if an approved reviewer has approved the pull request then the bot will approve the pull request analyst initiate the locking procedure and rebate support request into the into the repo so when we have a change which effects more than one repo we will we will trigger rebase is into the respective repos main branches while all of those repos are locked in fact all of the reports will be locked within that within the main repo and the 2nd party org this is because we need to ensure that all of the changes get merged and there are no conflicts so that we end up in an unknown state which which would result in us ending up in an unknown state our state is known so long as we have tested all of the PR's involved against the main branch I or the you know the latest commit before rebase. When all PR's in a set across repos are approved the bot will merge starting with the farthest downstream PR at it will specify somehow version information to the CIA so that the C I can block waiting for the commit which was in the original PR to be merged before continuing this will ensure that the CI jobs do not run against a slightly outdated version of the original the repo which the original PR was made against

Maintainer info

for support level two or three plugins which might break with the application of a PR we should have some bot or some workflow comment to highlight which plugins would break if this PR was applied this information is purely for maintainers well as well as ah it's mainly for maintainers so that they understand whether they should request additional work be done or slight modifications or ah whether we need to plan and create issues to to potentially for example breaking a support level two plug-in we may be OK with that we just need to make sure that we're tracking it
