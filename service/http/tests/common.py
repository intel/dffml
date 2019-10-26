import asyncio
from unittest.mock import patch
from contextlib import asynccontextmanager


class ServerRunner:
    def __init__(self):
        self.begin = asyncio.Queue()
        self.end = asyncio.Event()
        self.server_stopped = None

    async def start(self, coro):
        self.server_stopped = asyncio.create_task(coro)
        server_started = asyncio.create_task(self.begin.get())
        done, pending = await asyncio.wait(
            {self.server_stopped, server_started},
            return_when=asyncio.FIRST_COMPLETED,
        )
        # Raise issues if they happened
        for task in done:
            # This branch is only taken if tests fail
            if task is self.server_stopped:  # pragma: no cov
                exception = task.exception()
                if exception is not None:
                    raise exception
        return server_started.result()

    async def stop(self):
        self.end.set()
        await self.server_stopped

    @classmethod
    @asynccontextmanager
    async def patch(cls, server_cls):
        self = cls()
        with patch.object(
            server_cls, "RUN_YIELD_START", new=self.begin
        ), patch.object(server_cls, "RUN_YIELD_FINISH", new=self.end):
            yield self
            await self.stop()
