# Volume 0: Chapter 3: A Shell for a Ghost

Plan for this tutorial:

- [ ] We make existing bash shell save minimal system context
      chain via `$CONTEXT` specific herstory files, map to
      current working directory / tmux panes and any other
      metadata we have on the shell as well.
  - [ ] Can create entries and map metadata by leveraging
        `HISTTIMEFORMAT` to insert lookup info to metadata
        stored in alternate representation on disk.
- [ ]

Alice is the ghost in the shell. We know she's in there,
she's the communication of herstory. We're in the shell,
up until now we've been writing all our docs by hand. We
now have the ability

References:
- https://github.com/rcaloras/bash-preexec