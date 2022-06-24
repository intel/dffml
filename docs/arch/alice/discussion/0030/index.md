### Turtles all the way down

- [ ] Revisit the patchset with remote / local execution.
- [ ] Modify CLI to be executed as via effectively what is now `RunDataFlow(CMD)/run()`.
  - [ ] This is how we'll support running a dataflow from an HTTP handler, or from CLI, or anywhere, because we'll use our new trick about reaching into the parent input network context.