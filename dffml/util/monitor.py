# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import asyncio
from typing import List, Set, Any, Optional

from .log import LOGGER

LOGGER = LOGGER.getChild("monitor")


class Watchdog(object):

    LOGGER = LOGGER.getChild("Watchdog")

    def __init__(self) -> None:
        """
        Specifiy event types to ignore with ignore list.
        """
        self.queue: asyncio.Queue = asyncio.Queue()

    async def enqueue(self, event, msg):
        self.LOGGER.debug("put: %r", (event, msg))
        await self.queue.put((event, msg))

    async def events(self):
        event = ""
        while event != "done":
            event, msg = await self.queue.get()
            self.LOGGER.debug("got: %r", (event, msg))
            self.queue.task_done()
            if event == "done":
                await self.queue.join()
            yield event, msg


class Task(object):

    LOGGER = LOGGER.getChild("Task")

    def __init__(self, func=None, key: Any = "") -> None:
        coro = None
        if not func is None:
            coro = func(task=self)
            if not key:
                key = coro
        self.__key = key
        self.__coro = coro
        self.__lock = asyncio.Lock()
        # Previous updates so addded watchdogs get all updates ever
        self.__events: List[Any] = []
        self.__watchdogs: List[Watchdog] = []

    @property
    def key(self):
        return self.__key

    @property
    def coro(self):
        return self.__coro

    async def add_watchdog(self, watchdog: Watchdog):
        async with self.__lock:
            self.__watchdogs.append(watchdog)
            self.LOGGER.debug("[%r] adding watcher", self.__key)
            self.LOGGER.debug(
                "[%r] adding watcher backlog: %r", self.__key, self.__events
            )
            self.LOGGER.debug(
                "[%r] watchers: %r", self.__key, self.__watchdogs
            )
            async for event, msg in self.get_events():
                await watchdog.enqueue(event, msg)

    async def completed(self, result):
        async with self.__lock:
            self.LOGGER.debug("[%r] completed", self.__key)
            await self.append_event("done", result)
            for watchdog in self.__watchdogs:
                await watchdog.enqueue("done", result)
            self.__watchdogs = []

    async def update(self, msg, event="update"):
        async with self.__lock:
            self.LOGGER.debug("[%r] sending %s: %r", self.__key, event, msg)
            await self.append_event(event, msg)
            for watchdog in self.__watchdogs:
                await watchdog.enqueue(event, msg)

    async def log(self, fmt, *args):
        await self.update(fmt % args, event="log")

    async def append_event(self, event, msg):
        self.__events.append((event, msg))

    async def get_events(self):
        for event, msg in self.__events:
            yield event, msg

    async def complete(self):
        async for event, msg in self.events():
            if event == "done":
                self.LOGGER.debug("[%r] complete %r", self.__key, msg)
                return msg

    async def events(self):
        watchdog = Watchdog()
        await self.add_watchdog(watchdog)
        async for event, msg in watchdog.events():
            self.LOGGER.debug("[%r] got event %r: %r", self.__key, event, msg)
            yield event, msg

    async def status(self):
        async for event, msg in self.events():
            if event == "done":
                break
            elif event == "update":
                yield msg

    async def statuses(self):
        return [msg async for msg in self.status()]

    async def logs(self):
        return [msg async for event, msg in self.events() if event == "log"]


class Monitor(object):

    LOGGER = LOGGER.getChild("Monitor")

    def __init__(self):
        self.in_progress = {}
        self.lock = asyncio.Lock()
        self.log_lock = asyncio.Lock()

    async def task(self, key: Any):
        task = None
        async with self.lock:
            task = self.in_progress.get(key, None)
            if task is None:
                return
        return task

    async def complete(self, key: Any):
        task = await self.task(key)
        if task is None:
            return
        await task.complete()

    async def events(self, key: Any):
        task = await self.task(key)
        if task is None:
            return
        async for event, msg in task.events():
            yield event, msg

    async def status(self, key: Any):
        task = None
        async with self.lock:
            task = self.in_progress.get(key, None)
            if task is None:
                return
        async for msg in task.status():
            yield msg

    async def statuses(self, key: Any):
        return [msg async for msg in self.status(key)]

    async def log_status(self, key: Any):
        async for msg in self.status(key):
            self.LOGGER.debug("status [%r]: %r", key, msg)
            yield msg
        self.LOGGER.debug("log status [%r] is done", key)

    async def run_task(self, task: Task):
        self.LOGGER.debug("Started running %r", task.key)
        result = await task.coro  # type: ignore
        self.LOGGER.debug("Done running %r", task.key)
        async with self.lock:
            await task.completed(result)
            del self.in_progress[task.key]
        self.LOGGER.debug("Removed running %r", task.key)

    async def start(self, func, key: Any = "", mktask=Task):
        async with self.lock:
            if key in self.in_progress:
                self.LOGGER.debug("Already running %r", key)
                return
            task = mktask(func, key)
            self.in_progress[task.key] = task
            asyncio.ensure_future(self.run_task(task))
            return task
