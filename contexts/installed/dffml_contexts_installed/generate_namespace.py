for sysctx in SystemContext.load():
    # Ideally we would have load not setting propreties on the loaded classes.
    # TODO for name, sysctx in SystemContext.load_dict().items():
    name = sysctx.ENTRY_POINT_LABEL
    """
    sysctx.parents
    sysctx.upstream
    sysctx.overlay
    sysctx.orchestrator
    """

    # sysctx.variable_name('python')
    # sysctx.add_to_namespace(sys.modules[__name__])

    # In the event the deployment enviornment requested as not found
    # (aka an auto start operation when condition
    # "string.sysctx.deployment.unknown" is present as an input)

    def make_correct_python_callable(name, sysctx):
        sysctx.deployment("python")
        # TODO, if deployment has non-auto start operatations with
        def func():
            func.__name__ = name

        return func

    setattr(sys.modules[__name__], name, make_correct_python_callable(syctx))


# END **system_contexts/__init__.py** END
# END **wonderland/async.py** END

# from wonderland import Alice, alice
# from wonderland.async import Alice

# async with AliceSystemContext() as alice:
#     async with alice() as alice_ctx:
#         async for thought in alice_ctx.thoughts():
#         # async for thought in alice_ctx(): # .thoughts is the default

# async with Alice() as alice:
#     async for thought in alice:

# for thought in alice:
#     print(thought)

# alice = Alice()
# for thought in alice:
#     print(thought)

