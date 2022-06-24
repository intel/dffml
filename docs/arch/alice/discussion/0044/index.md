# Volume 0: Chapter 3: A Shell for a Ghost

Plan for this tutorial:

- [ ] We make existing bash shell save minimal system context
      chain via `$CONTEXT` specific herstory files, map to
      current working directory / tmux panes and any other
      metadata we have on the shell as well.
  - [ ] Can create entries and map metadata by leveraging
        `HISTTIMEFORMAT` to insert lookup info to metadata
        stored in alternate representation on disk.
  - [ ] Figure out how to redirect output with `bash-preexec`
        to capture commands executed and their output.
- [ ] Build `.ipynb` files into docs pages.
  - [ ] Filter commands to exit status success from herstory
        for the entries within `.ipynb`
  - [ ] Filter down to commands whos coverage has overlap with
        lines changed during capture.
- [ ] Use NLP models based off the videos to write the English
      language text between running of commands.
- [ ] Mention future tutorials
  - [ ] Evolve complexity of I/O watching to save files,
        database state, etc. via overlays to capture
        more complete context for analysis to deduplicate
        work within non-state of the art trains of thought.
  - [ ] Async comms for Alice to interact with you in your
        environment. Example: tmux message, in event of
        immediate attention required open a new window
        in tmux session and split pane to render of Alice
        on one side (right), then split top and bottom
        on the left is her message on top flashed above for
        10 seconds (Alert!, Message from Bob!). The pane is
        then closed and we pop into the chat for that person,
        unless we've already switch to the comms pane.
  - [ ] Async comms overlays to show how to have Alice
        communicate with other developers or people or
        systems which you might want to notify of your
        activities periodically on trigger.
    - [ ] Example flow where we notify other devs when we
          tag and push a new version of anything, it does
          this by publishing to a RSS feed and notifying
          any waiting websocket connections.

Alice is the ghost in the shell. We know she's in there,
she's the communication of herstory. We're in the shell,
up until now we've been writing all our docs by hand. We
now have the ability

References:
- https://github.com/rcaloras/bash-preexec