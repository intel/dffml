import asyncio

from . import high_level


def train(*args, **kwargs):
    return asyncio.run(high_level.train(*args, **kwargs))


train.__doc__ = (
    high_level.train.__doc__.replace("await ", "")
    .replace("async ", "")
    .replace("asyncio.run(main())", "main()")
    .replace("    >>> import asyncio\n", "")
    .replace(
        "    >>> from dffml import *\n",
        "    >>> from dffml import *\n    >>> from dffml.noasync import *\n",
    )
)


def accuracy(*args, **kwargs):
    return asyncio.run(high_level.accuracy(*args, **kwargs))


accuracy.__doc__ = (
    high_level.accuracy.__doc__.replace("await ", "")
    .replace("async ", "")
    .replace("asyncio.run(main())", "main()")
    .replace("    >>> import asyncio\n", "")
    .replace(
        "    >>> from dffml import *\n",
        "    >>> from dffml import *\n    >>> from dffml.noasync import *\n",
    )
)


def predict(*args, **kwargs):
    async_gen = high_level.predict(*args, **kwargs).__aiter__()

    loop = asyncio.new_event_loop()

    def cleanup():
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

    while True:
        try:
            yield loop.run_until_complete(async_gen.__anext__())
        except StopAsyncIteration:
            cleanup()
            return
        except:
            cleanup()
            raise


predict.__doc__ = (
    high_level.predict.__doc__.replace("await ", "")
    .replace("asynciterator", "iterator")
    .replace("async ", "")
    .replace("asyncio.run(main())", "main()")
    .replace("    >>> import asyncio\n", "")
    .replace(
        "    >>> from dffml import *\n",
        "    >>> from dffml import *\n    >>> from dffml.noasync import *\n",
    )
)


def save(*args, **kwargs):
    return asyncio.run(high_level.save(*args, **kwargs))


save.__doc__ = (
    high_level.save.__doc__.replace("await ", "")
    .replace("async ", "")
    .replace("asyncio.run(main())", "main()")
    .replace("    >>> import asyncio\n", "")
    .replace(
        "    >>> from dffml import *\n",
        "    >>> from dffml import *\n    >>> from dffml.noasync import *\n",
    )
)


def load(*args, **kwargs):
    async_gen = high_level.load(*args, **kwargs).__aiter__()

    loop = asyncio.new_event_loop()

    def cleanup():
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

    while True:
        try:
            yield loop.run_until_complete(async_gen.__anext__())
        except StopAsyncIteration:
            cleanup()
            return
        except:
            cleanup()
            raise


load.__doc__ = (
    high_level.load.__doc__.replace("await ", "")
    .replace("async ", "")
    .replace("asyncio.run(main())", "main()")
    .replace("    >>> import asyncio\n", "")
    .replace(
        "    >>> from dffml import *\n",
        "    >>> from dffml import *\n    >>> from dffml.noasync import *\n",
    )
)
