import tempfile

from dffml.util.testing.consoletest.commands import (
    CreateVirtualEnvCommand,
    ActivateVirtualEnvCommand,
    PipInstallCommand,
)


async def setup(ctx):
    """
    Create a virtualenv for every document
    """
    venvdir = ctx["stack"].enter_context(tempfile.TemporaryDirectory())

    ctx["venv"] = venvdir

    for command in [
        CreateVirtualEnvCommand(ctx["venv"]),
        ActivateVirtualEnvCommand(ctx["venv"]),
        PipInstallCommand(
            [
                "python",
                "-m",
                "pip",
                "install",
                "-U",
                "pip",
                "setuptools",
                "wheel",
                "dffml",
            ]
        ),
    ]:
        print()
        print("[setup] Running", ctx, command)
        print()
        await ctx["astack"].enter_async_context(command)
        await command.run(ctx)
