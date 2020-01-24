Contributing
============

Contributions can come in many forms, we always need help improving the
documentation. If you find issues with the documentation, usability, code, or
even a question, please open an
`issue <https://github.com/intel/dffml/issues/new/choose>`_ to let us know.

Contacting the Community
------------------------

You can get in touch with the DFFML community via the following channels.

- `Gitter Chat <https://gitter.im/dffml/community>`_

- `Weekly Meetings <https://intel.github.io/dffml/community.html>`_

  - Recordings: https://www.youtube.com/channel/UCorEDRWGikwBH3dsJdDK1qA

- Open an `issue <https://github.com/intel/dffml/issues/new/choose>`_

- Users of DFFML Discussion Mailing List

  - Ask by emailing: `dffml-users@lists.01.org <mailto:dffml-users@lists.01.org>`_

  - Subscribe: https://lists.01.org/postorius/lists/dffml-users.lists.01.org/

- Development of DFFML Discussion Mailing List

  - Send emails to: `dffml-dev@lists.01.org <mailto:dffml-dev@lists.01.org>`_

  - Subscribe: https://lists.01.org/postorius/lists/dffml-dev.lists.01.org/

What To Work On
---------------

GitHub issue labels will let you know what needs help and help you find a
project that fits your time budget. Thank you for your help!

- Estimated Time to Complete

  - `XS: Extra Short <https://github.com/intel/dffml/labels/tXS>`_

    - Find and replace, fix a spelling mistake, make a change that shouldn't
      break anything.

  - `S: Short <https://github.com/intel/dffml/labels/tS>`_

    - Changes that are pretty much localized to one package

  - `M: Medium <https://github.com/intel/dffml/labels/tM>`_

    - Changes in one package that require changes in other packages

  - `L: Long <https://github.com/intel/dffml/labels/tL>`_

    - Changes to core architecture or functionality, API breaking changes

  - `XL: Extra Long <https://github.com/intel/dffml/labels/tXL>`_

    - Re-write the codebase(s) in another language

- Priority

  - `p4 <https://github.com/intel/dffml/labels/p4>`_

    - Nice To Have

  - `p3 <https://github.com/intel/dffml/labels/p3>`_

    - Average Priority

  - `p2 <https://github.com/intel/dffml/labels/p2>`_

    - Medium Priority

  - `p1 <https://github.com/intel/dffml/labels/p1>`_

    - High Priority

  - `p0 <https://github.com/intel/dffml/labels/p0>`_

    - Critical Priority

Who's Working On What
---------------------

We all overcommit sometimes, here are the rules for how you can tell if you
should work on something, if someone else is already working on it, or if
someones work has been abandoned (they might not have time to tell us that they
don't have time to work on it anymore).

- Don't worry about asking if you can work on something.

- If you have started work on something but do not yet have a pull request

  - Comment saying you have started

  - If you don't open a draft/WIP pull request within 7 days, we will take that
    to mean you're not working on it anymore.

- If you see an open a draft/WIP pull request that hasn't had any activity on it
  for more than 21 days. The community should considered it abandoned.

  - If you are still working on it, comment on it saying so. It's okay to be in
    progress for a while, just make sure you let others know that you intend to
    complete it.

- If you see an abandoned pull request, you can work on the issue it is
  partaining to.

  - You must comment on the pull request to let others know that you intend to
    pick up the work.

  - You should consider picking up where the person left off by using the work
    they've posted.

    - Add a ``Co-authored-by`` tag to any of their commits that you change, and
      leave them as the author for any commits you don't change.

Communication Style
-------------------

Logs, screenshots, the command you were running, and any files involved make
it easier for other developers to replicate whatever happened so they can help
you fix the problem.

Even better than a screenshot is an
`asciicast <https://asciinema.org/docs/installation>`_. It lets you create a
recording of your terminal that can be shared via a asciinema.org link or sent
privately as a JSON file.

Creating an issue and uploading any files or screenshots is always encouraged.

Working on DFFML
----------------

.. toctree::
    :glob:
    :maxdepth: 2

    dev_env
    style
    codebase
    git
    testing
    docs
    subsystems
    debugging
