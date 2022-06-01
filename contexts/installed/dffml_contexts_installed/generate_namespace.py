import sys

import dffml

DEFAULT_DEPLOYMENT: str = "python.native"

for sysctx in dffml.SystemContext.load():
    # Ideally we would have load not setting propreties on the loaded classes.
    # TODO for name, sysctx in SystemContext.load_dict().items():
    setattr(
        sys.modules[__name__],
        sysctx.ENTRY_POINT_LABEL,
        # TODO(alice) Should probably set origin / use origin as python.caller
        # or something like that.
        sysctx.deployment(deployment_environment=DEFAULT_DEPLOYMENT),
    )

delattr(sys.modules[__name__], "dffml")
delattr(sys.modules[__name__], "sys")

# **system_contexts/__init__.py**
# **wonderland/async.py**

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

# TODO Pick this work back up later when we have more of an idea about how the
# CLI is working and how we do overlays on an entity to create a different
# version / evolution of that entity.

# alice = Alice()
# print(alice)
# breakpoint()
# for thought in alice:
#     print(thought)
