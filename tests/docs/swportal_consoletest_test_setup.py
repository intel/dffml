import tempfile

from dffml.util.testing.consoletest.commands import (
    CreateVirtualEnvCommand,
    ActivateVirtualEnvCommand,
    CDCommand,
)


async def setup(ctx):
    """
    Create a virtualenv for every document and CD into the root directory
    """
    venvdir = ctx["stack"].enter_context(tempfile.TemporaryDirectory())

    ctx["venv"] = venvdir

    for command in [
        CreateVirtualEnvCommand(ctx["venv"]),
        ActivateVirtualEnvCommand(ctx["venv"]),
        CDCommand(ctx["root"]),
    ]:
        print()
        print("[setup] Running", ctx, command)
        print()
        await ctx["astack"].enter_async_context(command)
        await command.run(ctx)
