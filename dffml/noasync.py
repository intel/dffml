import asyncio

from . import high_level


def train(*args, **kwargs):
    return asyncio.run(high_level.train(*args, **kwargs))


def accuracy(*args, **kwargs):
    return asyncio.run(high_level.accuracy(*args, **kwargs))


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
